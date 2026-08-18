from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Task:
    text: str
    priority: str
    category: str = 'general'
    due_date: str = ''


def parse_task_line(line: str) -> dict[str, str]:
    parts = [part.strip() for part in line.split('|')]
    text = parts[0] if parts else ''
    category = parts[1] if len(parts) > 1 and parts[1] else 'general'
    due_date = parts[2] if len(parts) > 2 and parts[2] else ''
    return {'text': text, 'category': category, 'due_date': due_date}


def parse_tasks_text(text: str) -> list[str]:
    items = text.replace(';', '\n').splitlines()
    return [' '.join(item.strip().split()) for item in items if item.strip()]


def clean_tasks(lines: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        item = ' '.join(line.strip().split())
        if item:
            cleaned.append(item)
    LOGGER.info('bot1: cleaned %s tasks', len(cleaned))
    return cleaned


def classify_priority(task: str) -> str:
    low = task.lower()
    if any(word in low for word in ('pagar', 'correo', 'responder', 'presupuesto', 'urgente')):
        return 'alta'
    if any(word in low for word in ('revisar', 'comprar', 'ordenar')):
        return 'media'
    return 'baja'


def organize_tasks(tasks: Iterable[str]) -> list[Task]:
    order = {'alta': 0, 'media': 1, 'baja': 2}
    classified: list[Task] = []
    for t in tasks:
        parsed = parse_task_line(t)
        classified.append(Task(
            text=parsed['text'],
            priority=classify_priority(parsed['text']),
            category=parsed['category'],
            due_date=parsed['due_date'],
        ))
    LOGGER.info('bot2: classified %s tasks', len(classified))
    return sorted(classified, key=lambda task: (order[task.priority], task.text.lower()))


def build_summary(tasks: list[Task]) -> str:
    if not tasks:
        return 'No se encontraron tareas.\n'
    lines = ['Resumen final', '===============', '']
    for idx, task in enumerate(tasks, start=1):
        meta = f' | {task.category}'
        if task.due_date:
            meta += f' | {task.due_date}'
        lines.append(f'{idx}. [{task.priority.upper()}]{meta} -> {task.text}')
    lines.append('')
    lines.append(f'Total de tareas: {len(tasks)}')
    summary = '\n'.join(lines) + '\n'
    LOGGER.info('bot3: generated summary for %s tasks', len(tasks))
    return summary


def run_pipeline(input_path: Path, output_path: Path) -> str:
    raw = input_path.read_text(encoding='utf-8').splitlines()
    LOGGER.info('input: read %s raw lines from %s', len(raw), input_path.name)
    cleaned = clean_tasks(raw)
    classified = organize_tasks(cleaned)
    summary = build_summary(classified)
    output_path.write_text(summary, encoding='utf-8')
    LOGGER.info('output: wrote %s', output_path.name)
    return summary
