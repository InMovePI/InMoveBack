"""
Compat layer: manter a API pública `search_foods` e `get_nutrients_for_grams`
mas delegar para o serviço local TACO (base interna core.models.FoodItem).

Isto mantém a assinatura pública usada pelas views enquanto usa dados locais
para pesquisa e cálculo de nutrientes.
"""
from typing import List, Dict
from . import taco_db


def search_foods(query: str, country: str | None = None, lang: str | None = None) -> List[Dict]:
    """Delegar para TACO (base local) e manter a assinatura pública."""
    return taco_db.search_foods(query, country=country, lang=lang)


def get_nutrients_for_grams(food_id_or_text: str, grams: float) -> Dict[str, float]:
    """Delegar para a base local TACO.

    O parâmetro pode ser um food_id (pk) ou texto de pesquisa — o serviço
    tentará resolver por id e, em seguida, por nome.
    """
    return taco_db.get_nutrients_for_grams(food_id_or_text, grams)
