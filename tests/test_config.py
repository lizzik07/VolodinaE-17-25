"""Проверки конфигурации без сетевых запросов."""

import contextlib
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
parse_args = __import__("main").parse_args


class ConfigTests(unittest.TestCase):
    """Проверяет корректные настройки и ошибочные аргументы."""

    def test_defaults(self):
        """Проверяет обязательное имя и значения по умолчанию."""
        args = parse_args(["--package", "A"])
        self.assertEqual(args.depth, 3)
        self.assertEqual(args.version, "latest")

    def test_errors(self):
        """Проверяет неверные значения всех входных параметров."""
        cases = [["--depth", "-1"], ["--depth", "abc"],
                 ["--depth", "101"], ["--url", "file:///tmp/x"],
                 ["--url", "http://example.org:wrong"],
                 ["--version", ""], ["--version", "a/b"],
                 ["--test-file", ""],
                 ["--reverse"], ["--package", "a b"]]
        for extra in cases:
            with self.subTest(extra=extra):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        parse_args(["--package", "A"] + extra)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args([])
