"""Проверки обхода, тестовых файлов и ошибок загрузки."""

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
graph_module = __import__("graph")
repository = __import__("repository")
application = __import__("main")


class GraphTests(unittest.TestCase):
    """Проверяет поведение BFS без обращения к сети."""

    def test_cycle(self):
        """Сохраняет цикл и не обрабатывает вершины повторно."""
        source = {"A": ["B", "C"], "B": ["D"],
                  "C": ["D"], "D": ["A"]}
        calls = []

        def load(package):
            """Регистрирует обращение к вершине."""
            calls.append(package)
            return source[package]

        result = graph_module.bfs_recursive(["A"], load, 10)
        self.assertEqual(result, source)
        self.assertEqual(calls, ["A", "B", "C", "D"])

    def test_depth(self):
        """Глубина ограничивает число переходов от корня."""
        source = {"A": ["B"], "B": ["C"], "C": []}
        self.assertEqual(graph_module.bfs_recursive(["A"], source.get, 0),
                         {"A": []})
        self.assertEqual(graph_module.bfs_recursive(["A"], source.get, 1),
                         {"A": ["B"], "B": []})

    def test_invalid_json(self):
        """Проверяет синтаксис JSON, типы и неизвестные вершины."""
        cases = ["{", "[]", "{}", '{"a": []}',
                 '{"A": "B"}', '{"A": ["B"]}', '{"A": [1]}']
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "graph.json"
            for data in cases:
                path.write_text(data)
                with self.subTest(data=data), self.assertRaises(ValueError):
                    repository.load_test_graph(path)

    def test_data_errors(self):
        """Отсутствие файла/пакета возвращает ненулевой статус."""
        fixture = Path(__file__).parent / "fixtures/isolated.json"
        cases = [["--test-file", str(fixture), "--package", "B"],
                 ["--test-file", "missing.json", "--package", "A"]]
        for args in cases:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(application.main(args), 1)

    def test_network_error(self):
        """Сетевая ошибка не подменяется пустым результатом."""
        with patch.object(repository, "request_json", side_effect=OSError):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(application.main(["--package", "demo"]), 1)
