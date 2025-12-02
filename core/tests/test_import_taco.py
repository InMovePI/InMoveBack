import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.models.fooditem import FoodItem


CSV_HEADER = """id,Alimento,Descrição,energia_kcal,um,proteína_g,lipídios_g,um2,carboidratos_g
1,Arroz branco cozido,Arroz cozido,130,100g,2.4,0.2,100g,28
2,Feijão carioca cozido,Feijão cozido,77,100g,4.3,0.5,100g,13.7
"""


CSV_FALLBACK = """1,Arroz branco cozido,Arroz cozido,130,100g,2.4,0.2,100g,28
2,Feijão carioca cozido,Feijão cozido,77,100g,4.3,0.5,100g,13.7
"""


CSV_MULTILINE = """ , ,Carbo- , 
Número,Alimento,Idrato,Umidade,Porcao
1,Arroz tipo 1,28.1,69.1,100g
"""


class ImportTacoCommandTests(TestCase):

    def setUp(self):
        FoodItem.objects.all().delete()

    def _make_tmp_csv(self, contents: str) -> str:
        fd, path = tempfile.mkstemp(suffix='.csv', text=True)
        os.close(fd)
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(contents)
        return path

    def test_import_with_header_detects_and_creates_items(self):
        path = self._make_tmp_csv(CSV_HEADER)

        out = StringIO()
        err = StringIO()
        call_command('import_taco', '--path', path, stdout=out, stderr=err)

        # Two rows should have been created
        count = FoodItem.objects.count()
        self.assertEqual(count, 2)

        # Output should contain success message mentioning created items
        out_val = out.getvalue()
        self.assertIn('Created=', out_val)

        os.remove(path)

    def test_import_with_malformed_no_header_fallback_parses_rows(self):
        path = self._make_tmp_csv(CSV_FALLBACK)

        out = StringIO()
        err = StringIO()
        call_command('import_taco', '--path', path, stdout=out, stderr=err)

        count = FoodItem.objects.count()
        self.assertEqual(count, 2)

        self.assertIn('Import finished via fallback', out.getvalue())

        os.remove(path)

    def test_import_quiet_mode_suppresses_output(self):
        path = self._make_tmp_csv(CSV_FALLBACK)

        out = StringIO()
        err = StringIO()
        call_command('import_taco', '--path', path, '--quiet', stdout=out, stderr=err)

        self.assertEqual(out.getvalue().strip(), '')
        self.assertEqual(err.getvalue().strip(), '')

        # Data still imported
        self.assertEqual(FoodItem.objects.count(), 2)

        os.remove(path)

    def test_import_multiline_header_parses_carbs(self):
        """Validate that multi-line header (e.g. 'Carbo-' + 'idrato') is aggregated and carbohydrate values are read."""
        path = self._make_tmp_csv(CSV_MULTILINE)

        out = StringIO()
        err = StringIO()
        call_command('import_taco', '--path', path, stdout=out, stderr=err)

        # One FoodItem should have been created with carbs=28.1
        self.assertEqual(FoodItem.objects.count(), 1)
        fi = FoodItem.objects.first()
        # floats are stored; allow a small delta
        self.assertAlmostEqual(float(fi.carbs), 28.1, places=2)

        os.remove(path)
