"""Проверки поиска потребителей по всему тестовому репозиторию."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
config = __import__("main")
application = __import__("main")
graph_module = __import__("main")


class ReverseTests(unittest.TestCase):
    """Проверяет уровни и циклы обратного поиска."""

    def test_reverse_depths(self):
        """Находит прямых и косвенных потребителей F."""
        path = Path(__file__).parent / "fixtures/repository.json"
        for depth, expected in [(0, {"F"}), (1, {"D", "E", "F"}),
                                (3, set("ABCDEF"))]:
            args = config.parse_args(["--package", "F", "--test-file",
                                      str(path), "--reverse", "--depth",
                                      str(depth)])
            _, graph = application.build_graph(args)
            self.assertEqual(set(graph), expected)

    def test_reverse_cycle(self):
        """Обратный обход цикла завершается и сохраняет его вершины."""
        source = {"A": ["B"], "B": ["C"], "C": ["A"]}
        reverse = graph_module.reverse_graph(source)
        result = graph_module.bfs_recursive(["A"], reverse.get, 10)
        self.assertEqual(result, reverse)

    def test_empty_reverse(self):
        """Пакет без потребителей остаётся единственной вершиной."""
        source = graph_module.reverse_graph({"A": ["B"], "B": []})
        self.assertEqual(graph_module.bfs_recursive(["A"], source.get, 3),
                         {"A": []})
