from django.db import models
from .dieta import Dieta

class Refeicao(models.Model):
    nome_refeicao = models.CharField(max_length=100)
    horario = models.TimeField()
    descricao = models.TextField()
    dieta = models.ForeignKey(Dieta, on_delete=models.CASCADE, related_name='refeicoes')
    
    def __str__(self):
        return f"{self.nome_refeicao} - {self.horario}"