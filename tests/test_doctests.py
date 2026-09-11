"""Примеры из документации модулей выполняются как тесты (doctest)."""
import doctest
import unittest

from funclab import checks, folding, mapping, pipeline, primes

MODULES = [checks, folding, primes, mapping, pipeline]


def load_tests(
    loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str
) -> unittest.TestSuite:
    for module in MODULES:
        tests.addTests(doctest.DocTestSuite(module))
    return tests
