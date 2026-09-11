"""Демонстрация: ``python -m funclab [файл протокола]``."""
import sys

from funclab.demo import main

sys.exit(main(sys.argv[1:]))
