from __future__ import annotations

import logging
from pathlib import Path
from src.pipeline import run_pipeline

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / 'input.txt'
OUTPUT_FILE = BASE_DIR / 'output.txt'
LOG_FILE = BASE_DIR / 'project.log'


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    setup_logging()
    summary = run_pipeline(INPUT_FILE, OUTPUT_FILE)
    print(summary, end='')


if __name__ == '__main__':
    main()
