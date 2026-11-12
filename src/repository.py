"""Прямое чтение метаданных npm и учебного JSON-репозитория."""

import json
import re
from urllib.parse import quote
from urllib.request import urlopen

from semver import select_version

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
