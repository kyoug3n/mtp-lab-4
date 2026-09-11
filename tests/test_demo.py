"""Тесты демонстрационного протокола reports/demo.txt."""
import unittest
from pathlib import Path

from funclab.demo import SECTIONS, build_sections, run_example

REPORT = Path(__file__).resolve().parent.parent / "reports" / "demo.txt"


class RunExampleTests(unittest.TestCase):
    def test_expression_statement_and_error(self) -> None:
        namespace: dict[str, object] = {}
        self.assertEqual(run_example("x = 6", namespace), [">>> x = 6"])
        self.assertEqual(run_example("x * 7", namespace), [">>> x * 7", "42"])
        self.assertEqual(run_example("x / 0", namespace), [
            ">>> x / 0", "ZeroDivisionError: division by zero",
        ])


class DemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lines = build_sections()

    def test_every_task_has_a_section(self) -> None:
        for title, _ in SECTIONS:
            self.assertIn(f"=== {title} ===", self.lines)

    def test_every_example_is_shown(self) -> None:
        for _, examples in SECTIONS:
            for source in examples:
                with self.subTest(source=source):
                    self.assertIn(f">>> {source}", self.lines)

    def test_committed_report_is_up_to_date(self) -> None:
        """Протокол в репозитории совпадает со свежим прогоном примеров.

        Штамп в начале файла (команда, ревизия, версия Python) не
        сравнивается: он описывает, где и когда протокол был получен, и
        отделён от разделов первой пустой строкой.
        """
        committed = REPORT.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            committed[committed.index(""):],
            self.lines,
            "reports/demo.txt устарел — выполните "
            "python -m funclab reports/demo.txt",
        )


if __name__ == "__main__":
    unittest.main()
