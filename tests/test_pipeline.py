import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.pipeline import clean_tasks, organize_tasks, build_summary, run_pipeline, parse_tasks_text, parse_task_line


class TestPipeline(unittest.TestCase):
    def test_clean_tasks(self):
        self.assertEqual(clean_tasks(['  hola  ', '', '  dos   espacios  ']), ['hola', 'dos espacios'])

    def test_organize_tasks_orders_by_priority(self):
        tasks = ['ordenar escritorio', 'pagar internet', 'comprar leche', 'leer libro']
        ordered = organize_tasks(tasks)
        self.assertEqual([t.text for t in ordered], ['pagar internet', 'comprar leche', 'ordenar escritorio', 'leer libro'])
        self.assertEqual([t.priority for t in ordered], ['alta', 'media', 'media', 'baja'])

    def test_build_summary_contains_totals(self):
        summary = build_summary(organize_tasks(['pagar internet']))
        self.assertIn('Resumen final', summary)
        self.assertIn('Total de tareas: 1', summary)

    def test_run_pipeline_writes_output_file(self):
        with TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            input_path = tmp / 'input.txt'
            output_path = tmp / 'output.txt'
            input_path.write_text('comprar leche\n\npagar internet\n', encoding='utf-8')
            summary = run_pipeline(input_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.read_text(encoding='utf-8'), summary)
            self.assertIn('pagar internet', summary)

    def test_parse_tasks_text_splits_lines_and_semicolons(self):
        self.assertEqual(
            parse_tasks_text('comprar pan; pagar internet\n\nresponder correo'),
            ['comprar pan', 'pagar internet', 'responder correo'],
        )

    def test_parse_tasks_text_supports_category_and_due_date(self):
        self.assertEqual(
            parse_tasks_text('pagar internet | finanzas | 2026-08-20'),
            ['pagar internet | finanzas | 2026-08-20'],
        )

    def test_parse_task_line_breaks_out_metadata(self):
        self.assertEqual(
            parse_task_line('pagar internet | finanzas | 2026-08-20'),
            {'text': 'pagar internet', 'category': 'finanzas', 'due_date': '2026-08-20'},
        )

    def test_organize_tasks_prioritizes_due_soon_first(self):
        tasks = [
            'comprar pan | casa | 2026-08-20',
            'pagar internet | finanzas | 2026-08-18',
            'responder correo | trabajo | 2026-08-19',
            'declarar impuestos | finanzas | 2026-08-17',
        ]
        ordered = organize_tasks(tasks)
        self.assertEqual([t.text for t in ordered], ['declarar impuestos', 'pagar internet', 'responder correo', 'comprar pan'])


if __name__ == '__main__':
    unittest.main()
