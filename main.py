from __future__ import annotations

from pathlib import Path

from bot1 import collect_and_clean
from bot2 import classify_priority
from bot3 import build_summary

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / 'input.txt'
OUTPUT_FILE = BASE_DIR / 'output.txt'


def read_input() -> list[str]:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f'No existe {INPUT_FILE.name}. Crea el archivo con tareas.')
    return INPUT_FILE.read_text(encoding='utf-8').splitlines()


def main() -> None:
    raw_lines = read_input()
    cleaned = collect_and_clean(raw_lines)
    classified = classify_priority(cleaned)
    summary = build_summary(classified)
    OUTPUT_FILE.write_text(summary, encoding='utf-8')
    print(summary)


if __name__ == '__main__':
    main()
