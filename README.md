# Organizador de tareas con 3 bots

Proyecto mínimo en Python para practicar un flujo en cadena.

## Qué hace

- **Bot 1** limpia la lista de entrada
- **Bot 2** clasifica por prioridad básica
- **Bot 3** genera el resumen final

## Archivos

- `src/pipeline.py`: lógica principal
- `main.py`: ejecuta el programa y crea `project.log`
- `input.txt`: entrada manual
- `output.txt`: salida generada
- `tests/`: pruebas básicas

## Uso

```bash
python main.py
```

## Pruebas

```bash
python -m unittest discover -s tests -p "test_*.py" -q
```
