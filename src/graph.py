"""Рекурсивный BFS по уровням с ограничением глубины."""

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
