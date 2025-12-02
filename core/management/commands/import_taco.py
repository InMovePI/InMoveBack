import csv
import logging
import os
from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models.fooditem import FoodItem

logger = logging.getLogger(__name__)


def _to_float(v: str) -> float:
    if v is None:
        return 0.0
    v = str(v).strip()
    if not v or v.upper() in ('NA', 'TR', 'TR?'):  # 'Tr' / 'NA'
        return 0.0
    # replace comma decimal separator
    v = v.replace(',', '.')
    try:
        return float(Decimal(v))
    except Exception:
        return 0.0


class Command(BaseCommand):
    help = 'Importa o arquivo core/data/taco.csv para a tabela core_fooditem'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Caminho para taco.csv (default core/data/taco.csv)')
        parser.add_argument('--update', action='store_true', help='Atualizar registros existentes')
        parser.add_argument('--quiet', action='store_true', help='Run quietly (suppress stdout/stderr prints)')

    def handle(self, *args, **options):
        path = options.get('path') or os.path.join('core', 'data', 'taco.csv')
        if not os.path.exists(path):
            self.stderr.write(self.style.ERROR(f'Arquivo não encontrado: {path}'))
            return

        created = 0
        updated = 0

        # Open with universal newline and use csv reader
        with open(path, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            rows = list(reader)

            # Determine header block (the TACO file uses a multi-line header in many cases).
            # Find first data row (where first column looks numeric) and treat all prior rows as header rows.
            header_row = None
            header = []
            header_rows = []
            data_start_idx = None
            for i, row in enumerate(rows):
                first = row[0].strip() if len(row) > 0 else ''
                if first.isdigit():
                    data_start_idx = i
                    break

            if data_start_idx is not None and data_start_idx > 0:
                header_rows = rows[:data_start_idx]
                data_rows = rows[data_start_idx:]
                # Build aggregated header columns by joining header_rows column-wise
                max_cols = max((len(r) for r in header_rows), default=0)
                agg_header = []
                for col in range(max_cols):
                    parts = []
                    for hr in header_rows:
                        if col < len(hr) and hr[col] and str(hr[col]).strip():
                            parts.append(str(hr[col]).strip())
                    agg_header.append(' '.join(parts).lower())
                header = agg_header
                # pick the first row of header_rows as representative for finding indexes later
                header_row = header_rows[-1]
            else:
                header_rows = []
                data_rows = rows
            header_keywords = {
                'alimento', 'descri', 'descrição', 'descricao', 'energia', 'kcal', 'proteína', 'proteina',
                'lip', 'lipídeos', 'lipideos', 'gord', 'carbo', 'porção', 'porcao', 'por'
            }

            def row_tokens(r):
                return [str(c).lower().strip() for c in r if c and str(c).strip()]

            def looks_like_number(s):
                if s is None:
                    return False
                s = str(s).strip().replace(',', '.')
                try:
                    float(s)
                    return True
                except Exception:
                    return False

            # If header_rows was not detected by numeric-first heuristic, try heuristics across any single row
            if not header_rows:
                for i, row in enumerate(rows):
                    tokens = ' '.join(row_tokens(row))
                    # count how many keyword substrings appear
                    matches = sum(1 for k in header_keywords if k in tokens)
                    if matches >= 2:
                        header_row = row
                        break

                    # if row contains one keyword, check the next row: if the next row has numeric values in likely positions,
                    # assume this row is a header
                    if matches == 1 and i + 1 < len(rows):
                        nxt = rows[i + 1]
                        # check if there are at least two numeric-like cells in the next row
                        num_count = sum(1 for c in nxt if looks_like_number(c))
                        if num_count >= 2:
                            header_row = row
                            break

            if not header_row:
                # fallback parsing: attempt to detect data rows where first column is numeric (row id)
                fh.seek(0)
                # reload rows we already read above
                # 'rows' variable already available
                data_rows = []
                for row in rows:
                    if not row:
                        continue
                    first = row[0].strip() if len(row) > 0 else ''
                    # detect rows that begin with a number (record entries)
                    if first.isdigit():
                        data_rows.append(row)

                if not data_rows:
                    if not options.get('quiet'):
                        self.stderr.write(self.style.ERROR('Não foi possível localizar o header no CSV e nenhum data-row identificado'))
                    return

                # process rows using default column positions as fallback
                name_i = 1
                energy_i = 3
                protein_i = 5
                fat_i = 6
                carbs_i = 8
                portion_i = None

                for row in data_rows:
                    if not row or all((not c or c.strip() == '') for c in row):
                        continue

                    name = row[name_i].strip() if name_i < len(row) else ''
                    if not name:
                        continue

                    kcal = _to_float(row[energy_i]) if energy_i < len(row) else 0.0
                    protein = _to_float(row[protein_i]) if protein_i < len(row) else 0.0
                    fat = _to_float(row[fat_i]) if fat_i < len(row) else 0.0
                    carbs = _to_float(row[carbs_i]) if carbs_i < len(row) else 0.0

                    portion = ''
                    weight = 100.0

                    fi_qs = FoodItem.objects.filter(name__iexact=name)
                    if fi_qs.exists():
                        fi = fi_qs.first()
                        if options.get('update'):
                            fi.portion = portion or fi.portion
                            fi.weight_grams = weight
                            fi.calories = kcal
                            fi.protein = protein
                            fi.carbs = carbs
                            fi.fat = fat
                            fi.save()
                            updated += 1
                    else:
                        FoodItem.objects.create(
                            name=name,
                            portion=portion or '100g',
                            weight_grams=weight,
                            calories=kcal,
                            protein=protein,
                            carbs=carbs,
                            fat=fat,
                            country='Brasil',
                            languages='pt',
                        )
                        created += 1

                if not options.get('quiet'):
                    self.stdout.write(self.style.SUCCESS(f'Import finished via fallback. Created={created} Updated={updated}'))
                return

            # Normalize header indexes (header variable may be aggregated or built from header_row)
            if not header:
                header = [h.lower().strip() for h in header_row]

            def index_of(*keys):
                for k in keys:
                    for i, h in enumerate(header):
                        if h and k in h:
                            return i
                return None

            name_i = index_of('descrição', 'alimento')
            energy_i = index_of('energia', 'kcal')
            protein_i = index_of('proteína')
            fat_i = index_of('lip', 'lipídeos', 'lipideos', 'gord')
            carbs_i = index_of('carbo')
            portion_i = index_of('porção', 'porcao', 'por')

            # Now iterate remaining rows and parse
            # If we built data_rows earlier, iterate those; otherwise iterate rows after header_row
            if data_rows and len(data_rows) > 0:
                iter_rows = data_rows
            else:
                iter_rows = rows[rows.index(header_row) + 1:]

            for row in iter_rows:
                if not row or all((not c or c.strip() == '') for c in row):
                        continue

                # Get name
                name = ''
                if name_i is not None and name_i < len(row):
                    name = row[name_i].strip()
                else:
                    # fallback use second column
                    if len(row) > 1:
                        name = row[1].strip()

                if not name:
                    continue

                kcal = _to_float(row[energy_i]) if energy_i is not None and energy_i < len(row) else 0.0
                protein = _to_float(row[protein_i]) if protein_i is not None and protein_i < len(row) else 0.0
                fat = _to_float(row[fat_i]) if fat_i is not None and fat_i < len(row) else 0.0
                carbs = _to_float(row[carbs_i]) if carbs_i is not None and carbs_i < len(row) else 0.0

                portion = ''
                if portion_i is not None and portion_i < len(row):
                    portion = row[portion_i].strip()

                # weight_grams - we default to 100g (TACO values are per 100g)
                weight = 100.0

                # Create or update
                fi_qs = FoodItem.objects.filter(name__iexact=name)
                if fi_qs.exists():
                    fi = fi_qs.first()
                    if options.get('update'):
                        fi.portion = portion or fi.portion
                        fi.weight_grams = weight
                        fi.calories = kcal
                        fi.protein = protein
                        fi.carbs = carbs
                        fi.fat = fat
                        fi.save()
                        updated += 1
                else:
                    FoodItem.objects.create(
                        name=name,
                        portion=portion or '100g',
                        weight_grams=weight,
                        calories=kcal,
                        protein=protein,
                        carbs=carbs,
                        fat=fat,
                        country='Brasil',
                        languages='pt',
                    )
                    created += 1

        if not options.get('quiet'):
            self.stdout.write(self.style.SUCCESS(f'Import finished. Created={created} Updated={updated}'))