from django import forms
from django.forms import inlineformset_factory

from .models import Exercicio, PlanoTreino, SessaoTreino, SessaoExercicio


class ExercicioForm(forms.ModelForm):
    class Meta:
        model = Exercicio
        fields = ['nome', 'descricao', 'grupo_muscular']
        labels = {
            'nome': 'Nome',
            'descricao': 'Descrição',
            'grupo_muscular': 'Grupo Muscular',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'grupo_muscular': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PlanoTreinoForm(forms.ModelForm):
    class Meta:
        model = PlanoTreino
        fields = ['aluno', 'descricao', 'inicio', 'final', 'status']
        labels = {
            'aluno': 'Aluno',
            'descricao': 'Descrição',
            'inicio': 'Início',
            'final': 'Final',
            'status': 'Status',
        }
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'inicio': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            'final': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class SessaoTreinoForm(forms.ModelForm):
    class Meta:
        model = SessaoTreino
        fields = ['nome', 'ordem', 'observacao']
        labels = {
            'nome': 'Nome',
            'ordem': 'Ordem',
            'observacao': 'Observação',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


SessaoExercicioFormSet = inlineformset_factory(
    SessaoTreino,
    SessaoExercicio,
    fields=['exercicio', 'series', 'repeticoes', 'carga', 'tempo_descanso', 'ordem'],
    labels={
        'exercicio': 'Exercício',
        'series': 'Séries',
        'repeticoes': 'Repetições',
        'carga': 'Carga',
        'tempo_descanso': 'Descanso (seg)',
        'ordem': 'Ordem',
    },
    widgets={
        'exercicio': forms.Select(attrs={'class': 'form-select'}),
        'series': forms.TextInput(attrs={'class': 'form-control'}),
        'repeticoes': forms.NumberInput(attrs={'class': 'form-control'}),
        'carga': forms.NumberInput(attrs={'class': 'form-control'}),
        'tempo_descanso': forms.NumberInput(attrs={'class': 'form-control'}),
        'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
    },
    extra=1,
    can_delete=True,
)