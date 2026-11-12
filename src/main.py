"""Этап 4: прямой и обратный рекурсивный обход зависимостей."""

import sys

from config import parse_args, print_config
from graph import bfs_recursive, candidate_graph, reverse_graph
from repository import NpmRepository, load_test_graph


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
        source = None
    if args.reverse:
        if source is None:
            source = candidate_graph(repository, root, args.candidates)
        loader = reverse_graph(source).__getitem__
    return root, bfs_recursive([root], loader, args.depth)


def main(argv=None):
    """Выводит граф и возвращает код завершения."""
    args = parse_args(argv)
    try:
        root, graph = build_graph(args)
        print_config(args)
        if args.reverse:
            print("Reverse dependencies:", sorted(set(graph) - {root}))
        for package, deps in graph.items():
            print(f"{package}: {deps}")
    except (OSError, ValueError, KeyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
