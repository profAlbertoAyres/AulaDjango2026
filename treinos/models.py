from django.db import models

from usuarios.models import Aluno


# Create your models here.
class Exercicio(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    grupo_muscular = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Exercício'
        verbose_name_plural = 'Exercícios'
        ordering = ['nome']

    def __str__(self):
        return  self.nome

class PlanoTreino(models.Model):
    STATUS_CHOICES = [
        ('A','Ativo'),
        ('F','Finalizado'),
        ('C','Cancelado'),
    ]
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE,
                              related_name='planos_treino')
    descricao = models.TextField(blank=True, null=True)
    inicio = models.DateField()
    final = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    class Meta:
        verbose_name = 'Plano de Treino'
        verbose_name_plural = 'Planos de treino'
        ordering = ['inicio','aluno']

    def __str__(self):
        return f'{self.aluno.nome} - {self.descricao}'

class SessaoTreino(models.Model):
    plano_treino = models.ForeignKey(PlanoTreino, on_delete=models.CASCADE,
                                     related_name='sessoes')
    nome = models.CharField(max_length=100)
    ordem = models.IntegerField()
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Sessão de Treino'
        verbose_name_plural = 'Sessões de treino'
        ordering = ['ordem']

    def __str__(self):
        return self.nome


class SessaoExercicio(models.Model):
    #chaves estrangeiras
    sessao_treino = models.ForeignKey(SessaoTreino, on_delete=models.CASCADE,
                                      related_name='exercicios_da_sessao')
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE,
                                  related_name='sessoes_aparece')
    #Atributos extras do relacionamento
    series = models.CharField(max_length=100)
    repeticoes = models.IntegerField()
    carga = models.DecimalField(max_digits=6, decimal_places=2,
                                blank=True, null=True)
    tempo_descanso = models.IntegerField(blank=True, null=True)
    ordem = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['ordem']