from __future__ import annotations


def build_summary(classified_tasks: list[dict[str, str]]) -> str:
    lines = ['Resumen final', '===============', '']
    if not classified_tasks:
        return 'No se encontraron tareas.\n'
    for idx, item in enumerate(classified_tasks, start=1):
        lines.append(f"{idx}. [{item['prioridad'].upper()}] {item['tarea']}")
    lines.append('')
    lines.append(f'Total de tareas: {len(classified_tasks)}')
    return '\n'.join(lines) + '\n'
