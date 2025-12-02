from typing import Dict, List, Optional
import logging

from core.models.fooditem import FoodItem

logger = logging.getLogger(__name__)


def _as_item(fi: FoodItem) -> Dict:
    return {
        'id': str(fi.id),
        'name': fi.name,
        'brand': '',
        'portion': fi.portion,
        'weight_grams': float(fi.weight_grams),
        'countries': fi.country,
        'languages': [fi.languages] if fi.languages else [],
        'nutrients': {
            'calories': float(fi.calories),
            'protein': float(fi.protein),
            'carbs': float(fi.carbs),
            'fat': float(fi.fat),
        }
    }


def search_foods(query: str, country: Optional[str] = None, lang: Optional[str] = None) -> List[Dict]:
    """Busca local na tabela FoodItem usando icontains.

    Retorna até 10 resultados, filtrando por country/lang quando possível.
    """
    if not query or not query.strip():
        return []

    # Default country behavior: if not provided, assume BR (Brasil)
    country = country or 'BR'

    qs = FoodItem.objects.all()
    q = query.strip()
    qs = qs.filter(name__icontains=q)[:10]

    results = []
    for fi in qs:
        # Optionally filter by country/lang - TACO entries should already be Brasil/pt
        if country:
            c = country.strip().lower()
            if c in ('br', 'bra', 'brazil', 'brasil'):
                # accept if product country indicates Brazil OR if language is Portuguese
                country_ok = any(x in fi.country.lower() for x in ('br', 'brazil', 'brasil'))
                lang_ok = bool(fi.languages and fi.languages.lower().startswith('pt'))
                if not (country_ok or lang_ok):
                    continue
        if lang:
            if lang.strip().lower().startswith('pt'):
                if not fi.languages or not fi.languages.lower().startswith('pt'):
                    continue

        results.append(_as_item(fi))

    return results


def get_nutrients_for_grams(food_id_or_text: str, grams: float) -> Dict[str, float]:
    """Resolve um FoodItem por id (pk) ou busca por nome; retorna macros proporcionais ao peso informado.

    Se não encontrado, retorna zeros.
    """
    if not food_id_or_text:
        return {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}

    fi = None
    # try id
    if str(food_id_or_text).isdigit():
        try:
            fi = FoodItem.objects.filter(pk=int(food_id_or_text)).first()
        except Exception:
            fi = None

    if fi is None:
        # fallback to name search
        fi = FoodItem.objects.filter(name__icontains=food_id_or_text).first()

    if not fi:
        return {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}

    factor = float(grams) / float(fi.weight_grams) if fi.weight_grams else 0.0
    return {
        'calories': round(fi.calories * factor, 4),
        'protein': round(fi.protein * factor, 4),
        'carbs': round(fi.carbs * factor, 4),
        'fat': round(fi.fat * factor, 4),
    }
