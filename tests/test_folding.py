"""Тесты факториала через reduce (Средн. 4) и общих проверок аргументов."""
import math
import unittest

from funclab.checks import (
    as_stream,
    check_callable,
    check_callables,
    check_non_negative_int,
)
from funclab.folding import factorial


class FactorialTests(unittest.TestCase):
    def test_matches_math_factorial(self) -> None:
        for n in range(1001):
            with self.subTest(n=n):
                self.assertEqual(factorial(n), math.factorial(n))

    def test_empty_product_is_one(self) -> None:
        self.assertEqual(factorial(0), 1)
        self.assertEqual(factorial(1), 1)

    def test_result_is_exact_integer(self) -> None:
        # Целые числа Python не переполняются: 100! имеет 158 цифр.
        result = factorial(100)
        self.assertIsInstance(result, int)
        self.assertEqual(len(str(result)), 158)

    def test_rejects_non_integers_including_bool(self) -> None:
        for value in (5.0, "5", None, True, False, 2j):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    factorial(value)  # type: ignore[arg-type]

    def test_rejects_negative(self) -> None:
        with self.assertRaisesRegex(ValueError, "получено -1$"):
            factorial(-1)


class CheckTests(unittest.TestCase):
    def test_accepts_zero_and_big_numbers(self) -> None:
        for value in (0, 1, 10**100):
            with self.subTest(value=value):
                check_non_negative_int(value, "n")

    def test_upper_bound_is_optional_and_inclusive(self) -> None:
        check_non_negative_int(9, "сколько", maximum=9)
        with self.assertRaisesRegex(
            ValueError, "^сколько: ожидалось целое число не больше 9, "
                        "получено 10$"
        ):
            check_non_negative_int(10, "сколько", maximum=9)

    def test_error_names_the_argument(self) -> None:
        with self.assertRaisesRegex(TypeError, "^сколько: "):
            check_non_negative_int("3", "сколько")
        with self.assertRaisesRegex(ValueError, "^сколько: "):
            check_non_negative_int(-3, "сколько")
        with self.assertRaisesRegex(TypeError, "^шаг 1: "):
            check_callable(None, "шаг 1")
        with self.assertRaisesRegex(TypeError, "^функция 2: "):
            check_callables([abs, 5], "функция")

    def test_as_stream_returns_iterator_and_names_the_argument(self) -> None:
        self.assertEqual(list(as_stream([1, 2], "данные")), [1, 2])
        with self.assertRaisesRegex(
            TypeError, "^данные: ожидался итерируемый объект, получено 42$"
        ) as caught:
            as_stream(42, "данные")
        # Исходная ошибка остаётся причиной.
        self.assertIsInstance(caught.exception.__cause__, TypeError)

    def test_check_callable_accepts_every_kind_of_function(self) -> None:
        for value in (abs, len, lambda x: x, str, math.sqrt, factorial):
            with self.subTest(value=value):
                check_callable(value, "функция")


if __name__ == "__main__":
    unittest.main()
