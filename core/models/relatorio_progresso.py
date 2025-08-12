from django.db import models
from .user import User


class RelatorioProgresso(models.Model):
    data = models.DateField()
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)
    percentual_gordura = models.DecimalField(max_digits=5, decimal_places=2)
    percentual_massa_magra = models.DecimalField(max_digits=5, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='relatorios_progresso')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.data}"