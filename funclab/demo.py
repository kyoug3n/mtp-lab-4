"""Демонстрация всех заданий в виде сеанса интерпретатора.

Запуск: ``python -m funclab`` печатает протокол на экран,
``python -m funclab reports/demo.txt`` записывает его в файл.

Примеры хранятся строками и выполняются ``eval``/``exec``, а в протокол
попадают вместе с результатом, как в интерактивном Python. Так показанный
код гарантированно совпадает с выполненным. Строки — константы этого
модуля, ввод пользователя здесь не выполняется.
"""
import platform
import subprocess
import sys
import traceback
from itertools import islice, takewhile
from pathlib import Path
from typing import Any

from funclab.folding import factorial
from funclab.mapping import map_all
from funclab.pipeline import keep, pipeline, take, transform
from funclab.primes import PrimeIterator, primes

SECTIONS: list[tuple[str, list[str]]] = [
    ("Средн. 4 — факториал через reduce", [
        "factorial(0), factorial(1), factorial(5), factorial(20)",
        "list(map(factorial, range(10)))",
        "len(str(factorial(1000)))  # цифр в 1000!",
        "factorial(-1)",
        "factorial(5.0)",
        "factorial(True)",
    ]),
    ("Средн. 6 — генератор простых чисел", [
        "list(islice(primes(), 15))",
        "list(takewhile(lambda p: p < 60, primes()))",
        "next(islice(primes(), 9999, None))  # 10 000-е простое",
        "generator = primes()",
        "next(generator), next(generator), next(generator)",
        "next(generator)",
    ]),
    ("Средн. 10 — несколько функций к каждому элементу через map", [
        "list(map_all([abs, lambda x: x * x, str], [-3, 4]))",
        "list(map_all([str.upper, len, str.isdigit], ['abc', '42']))",
        "list(islice(map_all([lambda p: p % 4, lambda p: p % 6], primes()),"
        " 6))",
        "rows = map_all([factorial], [3, -1])  # ошибки нет: map ленивый",
        "next(rows)",
        "next(rows)",
        "map_all([abs, 5], [1])  # а не функцию видно сразу",
    ]),
    ("Повыш. 5 — класс-итератор PrimeIterator", [
        "iterator = PrimeIterator()",
        "iter(iterator) is iterator",
        "next(iterator), next(iterator), next(iterator)",
        "list(islice(iterator, 5))  # продолжает с места остановки",
        "list(islice(PrimeIterator(), 10000)) == "
        "list(islice(primes(), 10000))",
    ]),
    ("Повыш. 9 — конвейер обработки данных", [
        "readings = ['  21.5', '', '# датчик 2', '19', '999', '-3.25',"
        " ' 18.0 ']",
        "clean = pipeline(transform(str.strip),"
        " keep(lambda s: s and not s.startswith('#')), transform(float),"
        " keep(lambda t: -50 <= t <= 60))",
        "list(clean(readings))",
        "list(clean(['10', '# конец']))  # конвейер можно запускать снова",
        "first_big = pipeline(keep(lambda p: p > 1000), take(3))",
        "list(first_big(primes()))",
        "list(pipeline(take(3), sum)([1, 2, 3, 4]))",
        "pipeline(take(1), 5)",
    ]),
]


def run_example(source: str, namespace: dict[str, Any]) -> list[str]:
    """Выполнить одну строку как интерактивный Python.

    Выражение печатается вместе с ``repr`` результата, инструкция
    (присваивание) — без результата, исключение — последней строкой
    трассировки, как её показывает интерпретатор.
    """
    lines = [f">>> {source}"]
    try:
        try:
            code = compile(source, "<demo>", "eval")
        except SyntaxError:
            exec(compile(source, "<demo>", "exec"), namespace)
        else:
            lines.append(repr(eval(code, namespace)))
    except Exception as error:  # показать любую ошибку, как интерпретатор
        lines.append(traceback.format_exception_only(error)[-1].rstrip())
    return lines


def build_sections() -> list[str]:
    """Все разделы протокола; каждый начинается с пустой строки."""
    namespace: dict[str, Any] = {
        "factorial": factorial,
        "primes": primes,
        "PrimeIterator": PrimeIterator,
        "map_all": map_all,
        "pipeline": pipeline,
        "keep": keep,
        "transform": transform,
        "take": take,
        "islice": islice,
        "takewhile": takewhile,
    }
    lines: list[str] = []
    for title, examples in SECTIONS:
        lines += ["", f"=== {title} ==="]
        for source in examples:
            lines += run_example(source, namespace)
    return lines


def git_revision() -> str:
    """Короткий хеш и дата текущего коммита (с пометкой о правках)."""
    try:
        revision = subprocess.run(
            ["git", "log", "-1", "--format=%h (%ci)"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "неизвестна (git недоступен)"
    if status:
        revision += " + незакоммиченные изменения"
    return revision


def build_report() -> str:
    """Штамп (до первой пустой строки) и разделы протокола."""
    header = [
        "Демонстрация лабораторной работы №4 (вариант 4)",
        "Команда: python -m funclab reports/demo.txt",
        f"Ревизия: {git_revision()}",
        f"Python: {platform.python_version()}",
        "Имена из пакета funclab и itertools импортированы заранее.",
    ]
    return "\n".join(header + build_sections()) + "\n"


def main(argv: list[str]) -> None:
    """Записать протокол в файл из ``argv`` или вывести его на экран."""
    report = build_report()
    if argv:
        Path(argv[0]).write_text(report, encoding="utf-8", newline="\n")
        print(f"Протокол записан в {argv[0]}")
    else:
        print(report, end="")


if __name__ == "__main__":
    main(sys.argv[1:])
