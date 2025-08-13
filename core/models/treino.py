from django.db import models
from .user import User


class Treino(models.Model):
    TIPO_CHOICES = [
        ("sedentario", "Sedentário"),
        ("leve", "Leve"),
        ("moderado", "Moderado"),
        ("intenso", "Intenso"),
    ]

    nome_treino = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_treino = models.DateField()
    duracao_minutos = models.PositiveIntegerField()
    descricao = models.CharField(max_length=150, blank=True, null=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="treinos",
    )
    exercicios = models.ManyToManyField(
        "Exercicio", through="TreinoExercicio", related_name="treinos"
    )  # Through faz a tabela de ligação ser a minha própria tabela, midia dms
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_treino} - {self.data_treino}"

    def duracao_formatada(self):
        horas = self.duracao_minutos // 60
        minutos = self.duracao_minutos % 60

        if horas > 0:
            return f"{horas}h {minutos}min"
        return f"{minutos}min"