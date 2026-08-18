from __future__ import annotations

import argparse
import logging
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

from src.pipeline import run_pipeline, parse_tasks_text, generate_summary_from_text

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
    parser.add_argument('--cli', action='store_true', help='Usa la versión de consola')
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


def run_cli(args: argparse.Namespace) -> None:
    tasks_text = get_tasks_text(args)
    if tasks_text is None:
        raise FileNotFoundError(f'No existe {args.input}. Crea el archivo o usa --tasks/--interactive.')
    tasks = parse_tasks_text(tasks_text)
    args.input.write_text('\n'.join(tasks) + ('\n' if tasks else ''), encoding='utf-8')
    summary = run_pipeline(args.input, args.output)
    print(summary, end='')


def run_gui() -> None:
    root = tk.Tk()
    root.title('Organizador de tareas con 3 bots')
    root.geometry('900x700')

    tk.Label(root, text='Pega tus tareas aquí (una por línea o separadas por ;)').pack(anchor='w', padx=12, pady=(12, 4))
    text_in = scrolledtext.ScrolledText(root, height=12, wrap='word')
    text_in.pack(fill='both', expand=False, padx=12, pady=(0, 12))
    text_in.insert('1.0', 'comprar pan | casa | 2026-08-20\npagar internet | finanzas | 2026-08-18\nresponder correo | trabajo | 2026-08-19\n')

    tk.Label(root, text='Resultado').pack(anchor='w', padx=12, pady=(0, 4))
    text_out = scrolledtext.ScrolledText(root, height=20, wrap='word', state='disabled')
    text_out.pack(fill='both', expand=True, padx=12, pady=(0, 12))

    def generate() -> None:
        raw = text_in.get('1.0', 'end').strip()
        if not raw:
            messagebox.showwarning('Sin tareas', 'Escribe al menos una tarea.')
            return
        summary = generate_summary_from_text(raw)
        OUTPUT_FILE.write_text(summary, encoding='utf-8')
        INPUT_FILE.write_text('\n'.join(parse_tasks_text(raw)) + '\n', encoding='utf-8')
        text_out.configure(state='normal')
        text_out.delete('1.0', 'end')
        text_out.insert('1.0', summary)
        text_out.configure(state='disabled')

    button_bar = tk.Frame(root)
    button_bar.pack(fill='x', padx=12, pady=(0, 12))
    tk.Button(button_bar, text='Organizar tareas', command=generate).pack(side='left')
    tk.Button(button_bar, text='Limpiar', command=lambda: (text_in.delete('1.0', 'end'), text_out.configure(state='normal'), text_out.delete('1.0', 'end'), text_out.configure(state='disabled'))).pack(side='left', padx=8)

    root.mainloop()


def main() -> None:
    setup_logging()
    args = parse_args()
    if args.cli:
        run_cli(args)
    else:
        run_gui()


if __name__ == '__main__':
    main()
