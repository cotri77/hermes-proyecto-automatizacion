from __future__ import annotations

import argparse
import logging
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

from src.pipeline import (
    run_pipeline,
    parse_tasks_text,
    generate_summary_from_text,
    build_board_summary,
    save_bot_state,
    load_bot_state,
)

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
    root.geometry('980x760')

    pending_tasks: list[str] = load_bot_state(BASE_DIR / 'bot1_state.json')
    completed_tasks: list[str] = load_bot_state(BASE_DIR / 'bot3_state.json')

    tk.Label(root, text='Pega tus tareas aquí (una por línea o separadas por ;)').pack(anchor='w', padx=12, pady=(12, 4))
    text_in = scrolledtext.ScrolledText(root, height=8, wrap='word')
    text_in.pack(fill='x', padx=12)
    text_in.insert('1.0', 'comprar pan | casa | 2026-08-20\npagar internet | finanzas | 2026-08-18\nresponder correo | trabajo | 2026-08-19\n')

    lists_frame = tk.Frame(root)
    lists_frame.pack(fill='both', expand=True, padx=12, pady=12)

    left = tk.Frame(lists_frame)
    left.pack(side='left', fill='both', expand=True, padx=(0, 6))
    tk.Label(left, text='Pendientes').pack(anchor='w')
    pending_list = tk.Listbox(left, selectmode='extended')
    pending_list.pack(fill='both', expand=True)

    right = tk.Frame(lists_frame)
    right.pack(side='left', fill='both', expand=True, padx=(6, 0))
    tk.Label(right, text='Completadas').pack(anchor='w')
    completed_list = tk.Listbox(right)
    completed_list.pack(fill='both', expand=True)

    tk.Label(root, text='Resultado').pack(anchor='w', padx=12, pady=(0, 4))
    text_out = scrolledtext.ScrolledText(root, height=14, wrap='word', state='disabled')
    text_out.pack(fill='both', expand=True, padx=12, pady=(0, 12))

    activity_var = tk.StringVar(value='Actividad: sin acciones todavía')
    activity_label = tk.Label(root, textvariable=activity_var, anchor='w', justify='left')
    activity_label.pack(fill='x', padx=12, pady=(0, 12))

    def refresh_views() -> None:
        board = build_board_summary(pending_tasks, completed_tasks)
        OUTPUT_FILE.write_text(board, encoding='utf-8')
        text_out.configure(state='normal')
        text_out.delete('1.0', 'end')
        text_out.insert('1.0', board)
        text_out.configure(state='disabled')
        pending_list.delete(0, 'end')
        for task in pending_tasks:
            pending_list.insert('end', task)
        completed_list.delete(0, 'end')
        for task in completed_tasks:
            completed_list.insert('end', task)

    def load_tasks() -> None:
        raw = text_in.get('1.0', 'end').strip()
        if not raw:
            messagebox.showwarning('Sin tareas', 'Escribe al menos una tarea.')
            return
        nonlocal pending_tasks, completed_tasks
        pending_tasks = parse_tasks_text(raw)
        completed_tasks = []
        INPUT_FILE.write_text('\n'.join(pending_tasks) + '\n', encoding='utf-8')
        save_bot_state(BASE_DIR / 'bot1_state.json', pending_tasks)
        save_bot_state(BASE_DIR / 'bot3_state.json', completed_tasks)
        activity_var.set(build_activity_log([
            ('Bot 1', f'cargó {len(pending_tasks)} tareas'),
            ('Bot 2', 'clasificará cuando marques una vista o generes resumen'),
            ('Bot 3', 'sin tareas completadas todavía'),
            ('Orquestador', 'sincronizó el estado inicial'),
        ]).strip())
        refresh_views()

    def mark_completed() -> None:
        selected = list(pending_list.curselection())
        if not selected:
            messagebox.showinfo('Nada seleccionado', 'Selecciona una o más tareas pendientes.')
            return
        nonlocal pending_tasks, completed_tasks
        selected_texts = [pending_tasks[i] for i in selected]
        for idx in reversed(selected):
            completed_tasks.append(pending_tasks.pop(idx))
        pending_tasks.sort(key=lambda t: t.lower())
        completed_tasks.sort(key=lambda t: t.lower())
        save_bot_state(BASE_DIR / 'bot1_state.json', pending_tasks)
        save_bot_state(BASE_DIR / 'bot3_state.json', completed_tasks)
        activity_var.set(build_activity_log([
            ('Bot 1', f'actualizó pendientes: {len(pending_tasks)}'),
            ('Bot 3', f'marcó completadas: {len(completed_tasks)}'),
            ('Orquestador', f'movió {len(selected_texts)} tarea(s) al estado completado'),
        ]).strip())
        refresh_views()
        messagebox.showinfo('Listo', f'Se marcaron {len(selected_texts)} tarea(s) como completadas.')

    def reset_all() -> None:
        nonlocal pending_tasks, completed_tasks
        pending_tasks = []
        completed_tasks = []
        text_in.delete('1.0', 'end')
        pending_list.delete(0, 'end')
        completed_list.delete(0, 'end')
        text_out.configure(state='normal')
        text_out.delete('1.0', 'end')
        text_out.configure(state='disabled')
        OUTPUT_FILE.write_text('', encoding='utf-8')
        save_bot_state(BASE_DIR / 'bot1_state.json', pending_tasks)
        save_bot_state(BASE_DIR / 'bot3_state.json', completed_tasks)
        activity_var.set('Actividad: tablero reiniciado por el orquestador')

    button_bar = tk.Frame(root)
    button_bar.pack(fill='x', padx=12, pady=(0, 12))
    tk.Button(button_bar, text='Cargar tareas', command=load_tasks).pack(side='left')
    tk.Button(button_bar, text='Marcar completada(s)', command=mark_completed).pack(side='left', padx=8)
    tk.Button(button_bar, text='Limpiar todo', command=reset_all).pack(side='left')

    load_tasks()
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
