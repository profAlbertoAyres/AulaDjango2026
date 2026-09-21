from django.contrib.auth.models import User
from django.db import models

# Create your models here.


TIPO_SEXO_CHOICES = [
    ('F','Feminino'),
    ('M','Masculino'),
    ('PNI', 'Não informar')
]

ESTADOS_CHOICES = [
    ('AC','Acre'),
    ('AL','Alagoas'),
    ('AP','Amapá'),
    ('AM','Amazonas'),
    ('BA','Bahia'),
    ('CE','Ceará'),
    ('DF','Distrito Federal'),
    ('ES','Espírito Santo'),
    ('GO','Goiás'),
    ('MA','Maranhão'),
    ('MT','Mato Grosso'),
    ('MS','Mato Grosso do Sul'),
    ('MG','Minas Gerais'),
    ('PA','Pará'),
    ('PB','Paraíba'),
    ('PR','Paraná'),
    ('PE','Pernambuco'),
    ('PI','Piauí'),
    ('RJ','Rio de Janeiro'),
    ('RN','Rio Grande do Norte'),
    ('RS','Rio Grande do Sul'),
    ('RO','Rondônia'),
    ('RR','Roraima'),
    ('SC','Santa Catarina'),
    ('SP','São Paulo'),
    ('SE','Sergipe'),
    ('TO','Tocantins')
]

class Aluno(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='aluno')
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=3, blank=True, null=True, choices=TIPO_SEXO_CHOICES)
    nascimento = models.DateField(blank=True, null=True)
    celular = models.CharField(max_length=20)
    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=150, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=150, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True,
                              choices=ESTADOS_CHOICES)
    objetivo = models.TextField(max_length=5000, blank=True, null=True)

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Personal(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE, related_name='personal')
    nome = models.CharField(max_length=100)
    cref = models.CharField(max_length=50)
    especialidade = models.TextField(blank=True, null=True)
    celular = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Personal trainer'
        verbose_name_plural = 'Personal trainers'
        ordering = ['nome']

    def __str__(self):
        return self.nome