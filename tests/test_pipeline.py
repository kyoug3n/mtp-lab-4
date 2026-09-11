"""Тесты конвейера обработки данных (Повыш. 9)."""
import unittest
from collections.abc import Callable, Iterator
from functools import reduce
from itertools import count
from typing import Any

from funclab.folding import factorial
from funclab.mapping import map_all
from funclab.pipeline import Step, keep, pipeline, take, transform
from funclab.primes import primes

IntFunction = Callable[[int], Any]

RAW_READINGS = ["  21.5", "", "# датчик 2", "19", "abc", "-3.25", " 18.0 "]


def is_number(text: str) -> bool:
    try:
        float(text)
    except ValueError:
        return False
    return True


class PipelineTests(unittest.TestCase):
    def test_processes_raw_text_data(self) -> None:
        clean = pipeline(
            transform(str.strip),
            keep(lambda line: line and not line.startswith("#")),
            keep(is_number),
            transform(float),
        )
        self.assertEqual(list(clean(RAW_READINGS)),
                         [21.5, 19.0, -3.25, 18.0])

    def test_matches_nested_builtins(self) -> None:
        steps = pipeline(keep(lambda x: x % 3), transform(lambda x: x * x))
        data = range(-50, 50)
        self.assertEqual(list(steps(data)),
                         list(map(lambda x: x * x, filter(lambda x: x % 3,
                                                          data))))

    def test_elements_pass_all_steps_one_by_one(self) -> None:
        events: list[str] = []

        def spy(name: str, function: IntFunction) -> IntFunction:
            def wrapper(x: int) -> Any:
                events.append(f"{name}({x})")
                return function(x)
            return wrapper

        odd_squares = pipeline(
            keep(spy("keep", lambda x: x % 2)),
            transform(spy("square", lambda x: x * x)),
            take(2),
        )
        self.assertEqual(list(odd_squares(range(100))), [1, 9])
        # Никаких промежуточных списков: 1 прошёл оба шага раньше, чем
        # проверили 2, а после второго результата элементы не запрашивались.
        self.assertEqual(events, ["keep(0)", "keep(1)", "square(1)",
                                  "keep(2)", "keep(3)", "square(3)"])

    def test_works_on_infinite_input(self) -> None:
        first_big = pipeline(keep(lambda p: p > 1000), take(3))
        self.assertEqual(list(first_big(primes())), [1009, 1013, 1019])
        self.assertEqual(list(first_big(count())), [1001, 1002, 1003])

    def test_result_is_lazy_iterator(self) -> None:
        result = pipeline(transform(lambda x: 1 // x))([1, 0])
        self.assertIsInstance(result, Iterator)
        self.assertEqual(next(result), 1)
        with self.assertRaises(ZeroDivisionError):
            next(result)

    def test_can_be_run_many_times(self) -> None:
        first_two = pipeline(take(2))
        self.assertEqual(list(first_two("abc")), ["a", "b"])
        self.assertEqual(list(first_two("xyz")), ["x", "y"])

    def test_no_steps_returns_data_unchanged(self) -> None:
        self.assertEqual(list(pipeline()([3, 1, 2])), [3, 1, 2])

    def test_pipeline_is_a_step_itself(self) -> None:
        square: Step = transform(lambda x: x * x)
        small: Step = keep(lambda x: x < 50)
        nested = pipeline(pipeline(square, small), take(3))
        flat = pipeline(square, small, take(3))
        self.assertEqual(list(nested(range(10))), list(flat(range(10))))

    def test_any_stream_function_is_a_step(self) -> None:
        # sorted читает весь поток и возвращает список — тоже годится.
        ordered = pipeline(sorted, take(3))
        self.assertEqual(list(ordered([5, 1, 4, 2])), [1, 2, 4])

    def test_combines_with_other_tasks(self) -> None:
        # Простые числа → пары (p, p!) через map_all → сумма p! через reduce.
        pairs = pipeline(
            take(4),
            lambda stream: map_all([lambda p: p, factorial], stream),
        )
        rows = list(pairs(primes()))
        self.assertEqual(rows, [(2, 2), (3, 6), (5, 120), (7, 5040)])
        total = reduce(lambda acc, row: acc + row[1], rows, 0)
        self.assertEqual(total, 2 + 6 + 120 + 5040)


class PipelineErrorTests(unittest.TestCase):
    def test_bad_step_is_rejected_when_building(self) -> None:
        with self.assertRaisesRegex(
            TypeError, "^шаг 2: ожидалась функция, получено 5$"
        ):
            pipeline(take(1), 5)  # type: ignore[arg-type]

    def test_step_arguments_are_checked(self) -> None:
        with self.assertRaisesRegex(TypeError, "^условие: "):
            keep(None)  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "^преобразование: "):
            transform("upper")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "^сколько: "):
            take(-1)
        with self.assertRaisesRegex(TypeError, "^сколько: "):
            take(2.0)  # type: ignore[arg-type]

    def test_step_returning_not_a_stream(self) -> None:
        total = pipeline(take(3), sum)  # type: ignore[arg-type]
        with self.assertRaisesRegex(
            TypeError, "^шаг 2: ожидался итерируемый объект, получено 3$"
        ):
            total([1, 1, 1, 1])

    def test_data_is_not_iterable(self) -> None:
        with self.assertRaisesRegex(TypeError, "^данные: .*получено 42$"):
            pipeline(take(1))(42)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
