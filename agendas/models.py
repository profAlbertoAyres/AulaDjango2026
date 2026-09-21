from django.db import models

from usuarios.models import Aluno


# Create your models here.

class Agenda(models.Model):
    STATUS_CHOICES = [
        ('AGENDADO','Agendado'),
        ('REALIZADO','Realizado'),
        ('CANCELADO','Cancelado')
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE,
                              related_name='agendamentos')
    data = models.DateField()
    inicio = models.TimeField()
    fim = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='AGENDADO')
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'
        ordering = ['data','inicio']

    def __str__(self):
        return f'{self.aluno.nome} - {self.data:%d/%m/%Y} - {self.inicio:%H:%M}'