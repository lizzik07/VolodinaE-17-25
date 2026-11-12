"""Настройки CLI и проверка входных параметров."""

import argparse
import re
from urllib.parse import urlparse

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
