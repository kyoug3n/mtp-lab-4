"""Тесты применения нескольких функций через map (Средн. 10)."""
import math
import unittest
from collections.abc import Callable, Iterator
from itertools import count, islice
from typing import Any

from funclab.folding import factorial
from funclab.mapping import map_all


class MapAllTests(unittest.TestCase):
    def test_each_function_to_each_item(self) -> None:
        functions = [abs, lambda x: x ** 2, factorial, math.sqrt]
        self.assertEqual(
            list(map_all(functions, [1, 4, 9])),
            [(1, 1, 1, 1.0), (4, 16, 24, 2.0), (9, 81, 362880, 3.0)],
        )

    def test_row_equals_calling_functions_by_hand(self) -> None:
        functions: list[Callable[[int], Any]] = [str, hex, bin, float]
        for row, item in zip(map_all(functions, range(100)), range(100)):
            with self.subTest(item=item):
                self.assertEqual(row, tuple(f(item) for f in functions))

    def test_functions_may_come_from_generator(self) -> None:
        # Генератор функций кончился бы после первого элемента, если бы
        # map_all обходил его на каждой строке.
        functions = (lambda x, k=k: x * k for k in (1, 2, 3))
        self.assertEqual(list(map_all(functions, [1, 10])),
                         [(1, 2, 3), (10, 20, 30)])

    def test_items_may_be_one_shot_or_infinite(self) -> None:
        rows = map_all([str], iter([1, 2]))
        self.assertEqual(list(rows), [("1",), ("2",)])
        self.assertEqual(list(islice(map_all([abs], count(-2)), 3)),
                         [(2,), (1,), (0,)])

    def test_result_is_lazy(self) -> None:
        calls: list[int] = []

        def record(x: int) -> int:
            calls.append(x)
            return x

        rows = map_all([record], [1, 2, 3])
        self.assertIsInstance(rows, Iterator)
        self.assertEqual(calls, [])
        next(rows)
        self.assertEqual(calls, [1])

    def test_arguments_are_checked_before_the_first_row(self) -> None:
        # Ленивы вычисления, а не проверка аргументов: и встроенный map,
        # и map_all отвергают негодный поток сразу, не дожидаясь next.
        with self.assertRaises(TypeError):
            map(abs, 5)  # type: ignore[call-overload]
        with self.assertRaises(TypeError):
            map_all([abs], 5)  # type: ignore[arg-type]
        # При годных аргументах вызов остаётся ленивым: бесконечный поток
        # принят, а элементы ещё не читались.
        rows = map_all([abs], count(-2))
        self.assertEqual(next(rows), (2,))

    def test_no_functions_give_empty_rows(self) -> None:
        self.assertEqual(list(map_all([], [1, 2])), [(), ()])

    def test_rejects_non_function_immediately(self) -> None:
        with self.assertRaisesRegex(
            TypeError, "^функция 2: ожидалась функция, получено 5$"
        ):
            map_all([abs, 5], [1])  # type: ignore[list-item]

    def test_arguments_that_are_not_streams(self) -> None:
        # Сообщения такие же, как у конвейера: имя аргумента впереди.
        with self.assertRaisesRegex(
            TypeError, "^элементы: ожидался итерируемый объект, получено 5$"
        ):
            map_all([abs], 5)  # type: ignore[arg-type]
        with self.assertRaisesRegex(
            TypeError, "^функции: ожидался итерируемый объект, "
        ):
            map_all(abs, [1])  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
