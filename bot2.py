from __future__ import annotations


def classify_priority(tasks: list[str]) -> list[dict[str, str]]:
    high_keywords = ('pagar', 'correo', 'responder', 'presupuesto', 'urgente')
    medium_keywords = ('revisar', 'comprar')
    classified: list[dict[str, str]] = []
    for task in tasks:
        low = task.lower()
        if any(keyword in low for keyword in high_keywords):
            priority = 'alta'
        elif any(keyword in low for keyword in medium_keywords):
            priority = 'media'
        else:
            priority = 'baja'
        classified.append({'tarea': task, 'prioridad': priority})
    order = {'alta': 0, 'media': 1, 'baja': 2}
    return sorted(classified, key=lambda item: (order[item['prioridad']], item['tarea'].lower()))
