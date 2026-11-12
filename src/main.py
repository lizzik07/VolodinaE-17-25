"""Вариант №6: визуализатор графа зависимостей npm."""

import sys

from config import parse_args
from graph import bfs_recursive, reverse_graph
from repository import NpmRepository, load_test_graph
from visualization import generate_graphviz


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
