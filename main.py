from __future__ import annotations

import argparse
import logging
from pathlib import Path
from src.pipeline import run_pipeline, parse_tasks_text

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Organizador de tareas con 3 bots')
    parser.add_argument('--tasks', help='Tareas separadas por ; o por saltos de línea')
    parser.add_argument('--interactive', action='store_true', help='Pega tus tareas y termina con una línea vacía')
    parser.add_argument('--input', type=Path, default=INPUT_FILE, help='Archivo de entrada (por defecto input.txt)')
    parser.add_argument('--output', type=Path, default=OUTPUT_FILE, help='Archivo de salida (por defecto output.txt)')
    return parser.parse_args()


def get_tasks_text(args: argparse.Namespace) -> str | None:
    if args.tasks:
        return args.tasks
    if args.interactive:
        print('Pega tus tareas, una por línea o separadas por ;. Termina con una línea vacía:')
        lines: list[str] = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        return '\n'.join(lines)
    if args.input.exists():
        return args.input.read_text(encoding='utf-8')
    return None


def main() -> None:
    setup_logging()
    args = parse_args()
    tasks_text = get_tasks_text(args)
    if tasks_text is None:
        raise FileNotFoundError(f'No existe {args.input}. Crea el archivo o usa --tasks/--interactive.')
    tasks = parse_tasks_text(tasks_text)
    args.input.write_text('\n'.join(tasks) + ('\n' if tasks else ''), encoding='utf-8')
    summary = run_pipeline(args.input, args.output)
    print(summary, end='')


if __name__ == '__main__':
    main()
