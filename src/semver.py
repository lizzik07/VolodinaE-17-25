"""Самостоятельное сопоставление версий и диапазонов npm SemVer."""

import re

CORE_SIZE = 3
MAJOR = 0
MINOR = 1
PATCH = 2
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
        index = MINOR if size > 1 else MAJOR
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
        return lower <= key < upper_bound(high_core, high_size - 1)
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
