from django.core.exceptions import ValidationError
from django.db import models

from usuarios.models import Aluno


# Create your models here.

STATUS_QUE_OCUPAM = ('SOLICITADO', 'AGENDADO', 'REALIZADO')
STATUS_ATIVOS = STATUS_QUE_OCUPAM + ('BLOQUEADO',)

class HorarioAtendimento(models.Model):
    DIAS = [(0, 'Segunda'), (1, 'Terça'), (2, 'Quarta'), (3, 'Quinta'),
            (4, 'Sexta'), (5, 'Sábado'), (6, 'Domingo')]

    dia_semana = models.IntegerField(choices=DIAS)
    inicio = models.TimeField()
    fim = models.TimeField()

    class Meta:
        verbose_name = 'Horário de atendimento'
        verbose_name_plural = 'Horários de atendimento'
        ordering = ['dia_semana', 'inicio']

    def clean(self):
        super().clean()
        if not (self.inicio and self.fim):
            return  # campos inválidos: o próprio formulário já acusa o erro

        if self.fim <= self.inicio:
            raise ValidationError('O horário de término deve ser depois do início.')

        sobrepostos = HorarioAtendimento.objects.filter(
            dia_semana=self.dia_semana,
            inicio__lt=self.fim,
            fim__gt=self.inicio,
        ).exclude(pk=self.pk)

        if sobrepostos.exists():
            raise ValidationError('Este período se sobrepõe a outro já cadastrado nesse dia.')

    def __str__(self):
        return f'{self.get_dia_semana_display()} - {self.inicio:%H:%M} às {self.fim:%H:%M}'
    

class Agenda(models.Model):
    STATUS_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('AGENDADO', 'Agendado'),
        ('REALIZADO', 'Realizado'),
        ('CANCELADO', 'Cancelado'),
        ('RECUSADO', 'Recusado'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE,
                              related_name='agendamentos',
                              null=True, blank=True)
    data = models.DateField()
    inicio = models.TimeField()
    fim = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='AGENDADO')
    observacao = models.TextField(blank=True, null=True)
    justificativa = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Agenda'
        verbose_name_plural = 'Agendas'
        ordering = ['data','inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['data', 'inicio'],
                condition=models.Q(status__in=STATUS_ATIVOS),
                name='agenda_horario_ativo_unico',
                violation_error_message='Já existe um agendamento ativo neste horário.',
            ),
        ]

    def clean(self):
        super().clean()
        if self.status == 'RECUSADO' and not self.justificativa:
            raise ValidationError({
                'justificativa': 'É obrigatório informar o motivo da recusa.'
            })
        if self.inicio and self.fim and self.fim <= self.inicio:
            raise ValidationError({
                'fim': 'O horário de término deve ser depois do início.'
            })
        if self.data and self.inicio and self.status in STATUS_ATIVOS:
            conflito = (
                Agenda.objects
                .filter(data=self.data, inicio=self.inicio, status__in=STATUS_ATIVOS)
                .exclude(pk=self.pk)
            )
            if conflito.exists():
                raise ValidationError('Já existe um agendamento ativo neste horário.')


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        nome = self.aluno.nome if self.aluno else 'Bloqueado'
        return f'{nome} - {self.data:%d/%m/%Y} - {self.inicio:%H:%M}'