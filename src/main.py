"""Этап 1: минимальный настраиваемый CLI-прототип."""

from config import parse_args, print_config


def main(argv=None):
    """Проверяет опции и выводит конфигурацию."""
    print_config(parse_args(argv))


if __name__ == "__main__":
    main()
