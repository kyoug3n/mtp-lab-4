"""Тесты факториала через reduce (Средн. 4) и общих проверок аргументов."""
import math
import unittest

from funclab.checks import check_callable, check_count
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
    def test_check_count_accepts_zero_and_big_numbers(self) -> None:
        for value in (0, 1, 10**100):
            with self.subTest(value=value):
                check_count(value, "n")

    def test_error_names_the_argument(self) -> None:
        with self.assertRaisesRegex(TypeError, "^сколько: "):
            check_count("3", "сколько")
        with self.assertRaisesRegex(ValueError, "^сколько: "):
            check_count(-3, "сколько")
        with self.assertRaisesRegex(TypeError, "^шаг 1: "):
            check_callable(None, "шаг 1")

    def test_check_callable_accepts_every_kind_of_function(self) -> None:
        for value in (abs, len, lambda x: x, str, math.sqrt, factorial):
            with self.subTest(value=value):
                check_callable(value, "функция")


if __name__ == "__main__":
    unittest.main()
