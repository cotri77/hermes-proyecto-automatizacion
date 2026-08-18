import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.pipeline import clean_tasks, organize_tasks, build_summary, run_pipeline


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


if __name__ == '__main__':
    unittest.main()
