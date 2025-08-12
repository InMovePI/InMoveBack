from django.db import models
from .user import User


class IngestaoAgua(models.Model):
    data = models.DateField()
    quantidade_ml = models.PositiveIntegerField()
    horario = models.TimeField()
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ingestoes_agua"
    )

    def __str__(self):
        return f"{self.quantidade_ml}ml - {self.data}"