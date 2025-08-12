from django.db import models


class Exercicio(models.Model):
    nome_exercicio = models.CharField(max_length=100)
    grupo_muscular = models.CharField(max_length=50)
    descricao = models.CharField(max_length=100)

    def __str__(self):
        return self.nome_exercicio