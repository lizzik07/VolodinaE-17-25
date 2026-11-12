"""Проверки вывода Graphviz и вывода DOT."""

import contextlib
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
visualization = __import__("visualization")
application = __import__("main")


class VisualizationTests(unittest.TestCase):
    """Проверяет изолированные вершины, экранирование и направление."""

    def test_isolated(self):
        """Пакет без связей объявляется отдельной вершиной."""
        self.assertIn('"A";', visualization.generate_graphviz({"A": []}))

    def test_direction(self):
        """При обратном обходе DOT показывает исходное направление."""
        dot = visualization.generate_graphviz({"F": ["D"], "D": []}, True)
        self.assertIn('"D" -> "F";', dot)
        self.assertNotIn('"F" -> "D";', dot)

    def test_escaping(self):
        """Кавычки в подписи не нарушают синтаксис DOT."""
        dot = visualization.generate_graphviz({'a"b': []})
        self.assertIn('"a\\"b";', dot)

    def test_default_output(self):
        """Обычный запуск выводит описание графа без лишних данных."""
        path = Path(__file__).parent / "fixtures/isolated.json"
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = application.main(["--package", "A", "--test-file",
                                       str(path)])
        self.assertEqual(status, 0)
        self.assertEqual(output.getvalue(),
                         'digraph Dependencies {\n    "A";\n}\n')
