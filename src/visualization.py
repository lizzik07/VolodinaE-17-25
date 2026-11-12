"""Текстовое представление ориентированного графа на языке DOT."""

import json


def generate_graphviz(graph, reverse=False):
    """Объявляет все вершины, сохраняя исходное направление зависимости."""
    lines = ["digraph Dependencies {"]
    for package in sorted(graph):
        lines.append(f"    {json.dumps(package)};")
        for dep in graph[package]:
            source, target = (dep, package) if reverse else (package, dep)
            lines.append(f"    {json.dumps(source)} -> {json.dumps(target)};")
    return "\n".join(lines + ["}"])
