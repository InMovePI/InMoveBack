from django.db import models
from .treino import Treino
from .exercicio import Exercicio


class TreinoExercicio(models.Model):
    treino = models.ForeignKey(Treino, on_delete=models.CASCADE)
    exercicio = models.ForeignKey(Exercicio, on_delete=models.PROTECT)
    series = models.PositiveIntegerField()
    repeticoes = models.PositiveIntegerField()
    carga_kg = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.treino.nome_treino} - {self.exercicio.nome_exercicio}"