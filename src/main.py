"""Этап 2: прямые зависимости заданной версии пакета."""

import sys

from config import parse_args, print_config
from repository import NpmRepository, load_test_graph


def main(argv=None):
    """Выводит конфигурацию и непосредственные зависимости."""
    args = parse_args(argv)
    print_config(args)
    try:
        if args.test_file:
            deps = load_test_graph(args.test_file)[args.package]
        else:
            repository = NpmRepository(args.url)
            root = repository.resolve(args.package, args.version)
            deps = repository.dependencies(root)
        print(deps)
    except (OSError, ValueError, KeyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
