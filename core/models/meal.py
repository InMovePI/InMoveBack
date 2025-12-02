from django.conf import settings
from django.db import models
from django.utils import timezone


class Meal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meals')
    title = models.CharField(max_length=150)
    date = models.DateField(default=timezone.localdate)
    time = models.TimeField()

    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self) -> str:
        return f"Meal(id={self.id}, title={self.title!r}, user={getattr(self.user, 'email', str(self.user))})"


class IngredientEntry(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='ingredients')
    food_name = models.CharField(max_length=200)
    weight_grams = models.FloatField()

    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    carbs = models.FloatField(default=0)

    def __str__(self) -> str:
        return f"IngredientEntry(id={self.id}, food={self.food_name!r}, weight={self.weight_grams}g)"
