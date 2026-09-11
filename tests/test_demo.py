"""Тесты демонстрации и протокола reports/demo.txt."""
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from funclab.demo import (
    SECTIONS,
    build_sections,
    git_revision,
    main,
    run_example,
)

REPORT = Path(__file__).resolve().parent.parent / "reports" / "demo.txt"


class RunExampleTests(unittest.TestCase):
    def test_expression_statement_and_error(self) -> None:
        namespace: dict[str, object] = {}
        self.assertEqual(run_example("x = 6", namespace), [">>> x = 6"])
        self.assertEqual(run_example("x * 7", namespace), [">>> x * 7", "42"])
        self.assertEqual(run_example("x / 0", namespace), [
            ">>> x / 0", "ZeroDivisionError: division by zero",
        ])


class CommandLineTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def run_main(self, argv: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(argv)
        return code, output.getvalue()

    def test_writes_the_file(self) -> None:
        path = self.directory / "demo.txt"
        code, output = self.run_main([str(path)])
        self.assertEqual(code, 0)
        self.assertIn(f"Протокол записан в {path}", output)
        text = path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("Демонстрация лабораторной"))
        # Перевод строки один и тот же на любой системе.
        with path.open(encoding="utf-8", newline="") as file:
            raw = file.read()
        self.assertNotIn("\r", raw)

    def test_without_arguments_prints_the_report(self) -> None:
        code, output = self.run_main([])
        self.assertEqual(code, 0)
        self.assertIn("=== " + SECTIONS[0][0] + " ===", output)

    def test_help_does_not_create_a_file(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            self.run_main(["--help"])
        self.assertEqual(caught.exception.code, 0)
        self.assertFalse(Path("--help").exists())

    def test_unwritable_path_reports_error(self) -> None:
        path = self.directory / "нет" / "папки.txt"
        code, output = self.run_main([str(path)])
        self.assertEqual(code, 1)
        self.assertIn(f"Не удалось записать {path}: ", output)

    def test_revision_does_not_depend_on_current_directory(self) -> None:
        here = Path.cwd()
        os.chdir(self.directory)
        try:
            elsewhere = git_revision()
        finally:
            os.chdir(here)
        self.assertEqual(elsewhere, git_revision())


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
