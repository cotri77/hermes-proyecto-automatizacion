from __future__ import annotations


def collect_and_clean(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        item = line.strip()
        if not item:
            continue
        item = ' '.join(item.split())
        cleaned.append(item)
    return cleaned
