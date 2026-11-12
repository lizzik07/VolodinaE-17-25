"""Проверки загрузки npm без настоящей сети."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
repository = __import__("main")
semver = __import__("main")


class VersionTests(unittest.TestCase):
    """Проверяет диапазоны и порядок версий npm."""

    def test_ranges(self):
        """Проверяет caret, tilde, wildcard, AND, OR и частичные версии."""
        cases = [("1.2.3", "^1.0.0", True),
                 ("2.0.0", "^1.0.0", False),
                 ("0.3.0", "^0.2.1", False),
                 ("1.3.0", "~1.2.0", False),
                 ("1.2.9", "1.2.x", True),
                 ("1.5.0", ">=1 <2", True),
                 ("3.0.0", "1.x || 3.x", True),
                 ("2.3.4", "1.2 - 2.3", True),
                 ("1.0.0-beta.1", "*", False),
                 ("1.0.0-beta.2", ">=1.0.0-beta.1 <2", True),
                 ("1.0.0", "^0", False)]
        for version, spec, expected in cases:
            with self.subTest(version=version, spec=spec):
                self.assertEqual(semver.satisfies(version, spec), expected)

    def test_versions_and_cache(self):
        """Вложенный пакет подбирается по диапазону, не по latest."""
        data = {"versions": {"1.0.0": {"dependencies": {"b": "^1"}},
                             "1.5.0": {}, "2.0.0": {}},
                "dist-tags": {"latest": "2.0.0"}}
        with patch.object(repository, "request_json") as get:
            get.return_value = data
            source = repository.NpmRepository("https://example.org")
            root = source.resolve("a", "1.0.0")
            self.assertEqual(source.dependencies(root), ["b@1.5.0"])
            source.dependencies(root)
            self.assertEqual(get.call_count, 2)

    def test_prerelease_order(self):
        """Числовые prerelease-компоненты сравниваются как числа."""
        self.assertLess(semver.version_key("1.0.0-beta.2"),
                        semver.version_key("1.0.0-beta.10"))
        self.assertLess(semver.version_key("1.0.0-rc.1"),
                        semver.version_key("1.0.0"))

    def test_alias(self):
        """Проверяет обычные и scoped npm aliases."""
        self.assertEqual(repository.alias_target("a", "npm:b@^1"),
                         ("b", "^1"))
        self.assertEqual(repository.alias_target("a", "npm:@s/b@~1"),
                         ("@s/b", "~1"))
