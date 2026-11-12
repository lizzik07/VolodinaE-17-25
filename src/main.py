"""Вариант №6: визуализатор графа зависимостей npm."""

import argparse
import json
import re
import sys
from urllib.parse import quote, urlparse
from urllib.request import urlopen


MIN_DEPTH = 0
MAX_DEPTH = 100
DEFAULT_DEPTH = 3
PACKAGE_PATTERN = r"(?:@[a-z0-9_.-]+/)?[a-z0-9_.-]+|[A-Z]+"


def nonempty(value):
    """Запрещает пустые значения параметров."""
    if not value.strip():
        raise argparse.ArgumentTypeError("значение не может быть пустым")
    return value


def depth_value(value):
    """Проверяет целую глубину и предел рекурсивного обхода."""
    try:
        depth = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("нужна целая глубина") from error
    if not MIN_DEPTH <= depth <= MAX_DEPTH:
        raise argparse.ArgumentTypeError(
            f"глубина должна быть от {MIN_DEPTH} до {MAX_DEPTH}"
        )
    return depth


def validate_names(parser, args):
    """Проверяет имена пакетов, версию или тег и адрес реестра."""
    names = [args.package]
    for name in names:
        if not re.fullmatch(PACKAGE_PATTERN, name):
            parser.error(f"неверное имя пакета: {name}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_-]*", args.version):
        parser.error("--version: требуется точная версия или тег")
    address = urlparse(args.url)
    if address.scheme not in {"http", "https"} or not address.hostname:
        parser.error("--url: требуется HTTP(S)-адрес реестра")
    try:
        address.port
    except ValueError:
        parser.error("--url: неверный номер порта")
    if args.reverse and not args.test_file:
        parser.error("для обратного поиска укажите файл тестового репозитория")


def parse_args(argv=None):
    """Разбирает обязательные и дополнительные опции запуска."""
    parser = argparse.ArgumentParser(description="Граф зависимостей npm")
    parser.add_argument("--package", required=True, type=nonempty)
    parser.add_argument("--version", default="latest", type=nonempty)
    parser.add_argument("--url", default="https://registry.npmjs.org")
    parser.add_argument("--depth", type=depth_value, default=DEFAULT_DEPTH)
    parser.add_argument("--test-file", type=nonempty)
    parser.add_argument("--reverse", action="store_true")
    args = parser.parse_args(argv)
    validate_names(parser, args)
    return args


CORE_SIZE = 3
MAJOR = 0
MINOR = 1
TWO_COMPONENTS = 2
VERSION_PATTERN = r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
VERSION_PATTERN += r"(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?"


def version_key(value):
    """Возвращает сравнимый ключ SemVer, учитывая prerelease."""
    match = re.fullmatch(VERSION_PATTERN, value)
    if not match:
        raise ValueError(f"неверная версия SemVer: {value}")
    core = tuple(int(part) for part in match.groups()[:CORE_SIZE])
    prerelease = match.group(CORE_SIZE + 1)
    if prerelease is None:
        return core + (True, ())
    parts = tuple((False, int(part)) if part.isdigit() else (True, part)
                  for part in prerelease.split("."))
    return core + (False, parts)


def partial(value):
    """Разбирает частичную версию и считает явно заданные компоненты."""
    clean = value.lstrip("v=")
    core = clean.split("-", 1)[0].split("+", 1)[0]
    parts = core.split(".")
    if len(parts) > CORE_SIZE:
        raise ValueError(f"неверный диапазон: {value}")
    numbers = []
    for part in parts:
        if part.lower() in {"x", "*", ""}:
            break
        if not part.isdigit():
            raise ValueError(f"неподдерживаемый диапазон: {value}")
        numbers.append(int(part))
    size = len(numbers)
    numbers += [0] * (CORE_SIZE - size)
    suffix = "-" + clean.split("-", 1)[1] if "-" in clean else ""
    return tuple(numbers), size, suffix


def format_core(core):
    """Форматирует три компонента версии."""
    return ".".join(str(part) for part in core)


def upper_bound(core, index):
    """Получает исключающую верхнюю границу диапазона."""
    result = list(core)
    result[index] += 1
    for position in range(index + 1, CORE_SIZE):
        result[position] = 0
    return version_key(format_core(result) + "-0")


def compatible_upper(core, size, operator):
    """Вычисляет верхнюю границу caret и tilde."""
    if operator == "~":
        index = MINOR if size >= TWO_COMPONENTS else MAJOR
    else:
        nonzero = [index for index in range(size) if core[index]]
        index = nonzero[0] if nonzero else max(MAJOR, size - 1)
    return upper_bound(core, index)


def compare(left, operator, right):
    """Сравнивает ключи версий заданным оператором."""
    operations = {"=": left == right, ">": left > right,
                  ">=": left >= right, "<": left < right,
                  "<=": left <= right}
    return operations[operator]


def token_matches(key, token):
    """Проверяет один comparator, wildcard, caret или tilde."""
    match = re.fullmatch(r"(\^|~|>=|<=|>|<|=)?(.+)", token)
    if not match:
        raise ValueError(f"неверное условие диапазона: {token}")
    operator, value = match.groups()
    operator = operator or "="
    core, size, suffix = partial(value)
    if not size:
        return operator not in {"<", ">"}
    lower = version_key(format_core(core) + suffix)
    if operator in {"^", "~"}:
        return lower <= key < compatible_upper(core, size, operator)
    if size < CORE_SIZE:
        upper = upper_bound(core, size - 1)
        if operator == "=":
            return lower <= key < upper
        if operator == "<=":
            return key < upper
        if operator == ">":
            return key >= upper
    return compare(key, operator, lower)


def hyphen_matches(key, text):
    """Проверяет включающий диапазон вида 1.2.3 - 2.0.0."""
    start, finish = text.split(" - ")
    low_core, _, low_suffix = partial(start)
    high_core, high_size, high_suffix = partial(finish)
    lower = version_key(format_core(low_core) + low_suffix)
    if high_size < CORE_SIZE:
        upper = upper_bound(high_core, high_size - 1)
        return lower <= key < upper
    upper = version_key(format_core(high_core) + high_suffix)
    return lower <= key <= upper


def prerelease_allowed(key, clause):
    """Исключает prerelease без явного prerelease того же ядра."""
    if key[CORE_SIZE]:
        return True
    tokens = re.findall(VERSION_PATTERN, clause)
    return any(tuple(map(int, token[:CORE_SIZE])) == key[:CORE_SIZE]
               and token[CORE_SIZE] for token in tokens)


def satisfies(version, requirement):
    """Проверяет OR/AND, точные, частичные и prerelease-диапазоны."""
    key = version_key(version)
    for clause in requirement.strip().split("||"):
        clause = clause.strip() or "*"
        if not prerelease_allowed(key, clause):
            continue
        if " - " in clause:
            matched = hyphen_matches(key, clause)
        else:
            clause = re.sub(r"([<>=~^]+)\s+", r"\1", clause)
            matched = all(token_matches(key, token)
                          for token in clause.split())
        if matched:
            return True
    return False


def select_version(metadata, requirement):
    """Выбирает тег или наибольшую опубликованную подходящую версию."""
    versions = metadata.get("versions", {})
    tagged = metadata.get("dist-tags", {}).get(requirement)
    if tagged in versions:
        return tagged
    matches = [version for version in versions
               if satisfies(version, requirement)]
    if not matches:
        raise ValueError(f"нет версии, подходящей под {requirement}")
    return max(matches, key=version_key)


REQUEST_TIMEOUT = 20
REQUEST_ATTEMPTS = 3
LAST_ATTEMPT = REQUEST_ATTEMPTS - 1


def request_json(url):
    """Читает HTTP JSON; сетевые ошибки передаются вызывающему коду."""
    for attempt in range(REQUEST_ATTEMPTS):
        try:
            with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except OSError:
            if attempt == LAST_ATTEMPT:
                raise


def load_test_graph(filepath):
    """Проверяет полный граф с именами из больших латинских букв."""
    with open(filepath, encoding="utf-8") as source:
        graph = json.load(source)
    if not isinstance(graph, dict) or not graph:
        raise ValueError("тестовый граф: нужен непустой объект JSON")
    for package, deps in graph.items():
        if not re.fullmatch(r"[A-Z]+", package):
            raise ValueError("имена тестовых пакетов: большие латинские буквы")
        if not isinstance(deps, list):
            raise ValueError(f"{package}: нужен список зависимостей")
        if any(not isinstance(dep, str) or dep not in graph for dep in deps):
            raise ValueError(f"{package}: неизвестная зависимость")
    return {package: sorted(set(deps)) for package, deps in graph.items()}


def alias_target(package, requirement):
    """Разбирает registry alias npm:имя@диапазон без запуска npm."""
    if not requirement.startswith("npm:"):
        return package, requirement
    target = requirement[len("npm:"):]
    name, separator, spec = target.rpartition("@")
    if not separator or not name:
        return target, "*"
    return name, spec


class NpmRepository:
    """Кэширует метаданные и различает вершины по имени и версии."""

    def __init__(self, base_url):
        """Создаёт кэши реестра и идентификаторов вершин."""
        self.base_url = base_url.rstrip("/")
        self.metadata = {}
        self.nodes = {}

    def resolve(self, package, requirement):
        """Выбирает подходящую версию и возвращает идентификатор вершины."""
        package, requirement = alias_target(package, requirement)
        if package not in self.metadata:
            url = self.base_url + "/" + quote(package, safe="@")
            self.metadata[package] = request_json(url)
        metadata = self.metadata[package]
        if not isinstance(metadata, dict) or "versions" not in metadata:
            raise ValueError(f"{package}: реестр не вернул версии пакета")
        version = select_version(metadata, requirement)
        identifier = f"{package}@{version}"
        self.nodes[identifier] = metadata["versions"][version]
        return identifier

    def dependencies(self, identifier):
        """Разрешает диапазоны dependencies для конкретной версии узла."""
        deps = self.nodes[identifier].get("dependencies", {})
        if not isinstance(deps, dict):
            raise ValueError(f"{identifier}: неверное поле dependencies")
        if any(not isinstance(value, str) for value in deps.values()):
            raise ValueError(f"{identifier}: неверный диапазон зависимости")
        return sorted({self.resolve(name, spec)
                       for name, spec in deps.items()})


ROOT_LEVEL = 0


def bfs_recursive(packages, get_deps, max_depth, graph=None, level=ROOT_LEVEL):
    """Обходит каждую вершину один раз, сохраняя циклические связи."""
    if graph is None:
        graph = {}
    current = sorted(set(packages) - graph.keys())
    if not current:
        return graph
    next_level = set()
    for package in current:
        deps = sorted(set(get_deps(package))) if level < max_depth else []
        graph[package] = deps
        next_level.update(deps)
    if level < max_depth:
        bfs_recursive(next_level, get_deps, max_depth, graph, level + 1)
    return graph


def reverse_graph(graph):
    """Разворачивает связи перед обходом обратных зависимостей."""
    result = {package: [] for package in graph}
    for package, deps in graph.items():
        for dep in deps:
            result.setdefault(dep, []).append(package)
    return {package: sorted(set(deps)) for package, deps in result.items()}


def generate_graphviz(graph, reverse=False):
    """Объявляет все вершины, сохраняя исходное направление зависимости."""
    lines = ["digraph Dependencies {"]
    for package in sorted(graph):
        lines.append(f"    {json.dumps(package)};")
        for dep in graph[package]:
            source, target = (dep, package) if reverse else (package, dep)
            lines.append(f"    {json.dumps(source)} -> {json.dumps(target)};")
    return "\n".join(lines + ["}"])


def build_graph(args):
    """Выбирает источник и выполняет обход от исходного пакета."""
    if args.test_file:
        source = load_test_graph(args.test_file)
        if args.package not in source:
            raise ValueError("исходный пакет отсутствует в тестовом графе")
        root = args.package
        loader = source.__getitem__
    else:
        repository = NpmRepository(args.url)
        root = repository.resolve(args.package, args.version)
        loader = repository.dependencies
    if args.reverse:
        loader = reverse_graph(source).__getitem__
    return root, bfs_recursive([root], loader, args.depth)


def print_result(args, root, graph):
    """Выводит обратные зависимости и описание графа на языке DOT."""
    if args.reverse:
        print("Reverse dependencies:", sorted(set(graph) - {root}))
    print(generate_graphviz(graph, args.reverse))


def main(argv=None):
    """Возвращает ненулевой код при неверных данных или ошибке сети."""
    args = parse_args(argv)
    try:
        root, graph = build_graph(args)
        print_result(args, root, graph)
    except (OSError, ValueError, KeyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
