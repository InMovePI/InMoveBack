from django.db import models


class FoodItem(models.Model):
    """Dados de alimento carregados a partir da TACO (banco local).

    Campos principais:
    - name: nome do alimento
    - portion: descrição da porção (quando disponível)
    - weight_grams: peso da porção em gramas (padrão: 100g)
    - calories, protein, carbs, fat: macros por porção (peso especificado)
    - country: origem (TACO -> Brasil)
    - languages: idioma(s) (ex.: 'pt')
    """

    name = models.CharField(max_length=300)
    portion = models.CharField(max_length=200, blank=True, default='100g')
    weight_grams = models.FloatField(default=100.0)

    calories = models.FloatField(default=0.0)
    protein = models.FloatField(default=0.0)
    carbs = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)

    # meta info
    country = models.CharField(max_length=80, default='Brasil')
    languages = models.CharField(max_length=50, default='pt')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return f"FoodItem(id={self.id}, name={self.name!r})"
