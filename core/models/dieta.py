from django.db import models
from .user import User


class Dieta(models.Model):
    OBJETIVO_CHOICES = [
        ('emagrecimento', 'Emagrecimento'),
        ('hipertrofia', 'Hipertrofia'),
        ('manutencao', 'Manutenção'),
    ]

    objetivo = models.CharField(max_length=20, choices=OBJETIVO_CHOICES)
    descricao = models.CharField(max_length=100)
    data_inicio = models.DateField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dietas")

    def __str__(self):
        return f"{self.objetivo} - {self.usuario.name}"