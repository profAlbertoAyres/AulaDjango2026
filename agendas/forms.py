from django import forms
from .models import Agenda


class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['aluno', 'data', 'inicio', 'fim', 'observacao']
        widgets = {
            'aluno': forms.Select(attrs={'class': 'form-control'}),
            'data': forms.HiddenInput(),
            'inicio': forms.HiddenInput(),
            'fim': forms.HiddenInput(),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        # status não aparece no form: entra sempre como 'AGENDADO' (default do model)

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        inicio = cleaned_data.get('inicio')
        fim = cleaned_data.get('fim')

        if not (data and inicio and fim):
            return cleaned_data

        if fim <= inicio:
            raise forms.ValidationError('O horário de término deve ser depois do início.')

        conflito = Agenda.objects.filter(
            data=data,
            inicio__lt=fim,
            fim__gt=inicio,
        ).exclude(status__in=['CANCELADO', 'RECUSADO'])

        if self.instance.pk:
            conflito = conflito.exclude(pk=self.instance.pk)

        if conflito.exists():
            raise forms.ValidationError('Já existe um agendamento nesse horário.')

        return cleaned_data


class RecusaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['justificativa']
        widgets = {
            'justificativa': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


from .models import Agenda, HorarioAtendimento


class HorarioAtendimentoForm(forms.ModelForm):
    class Meta:
        model = HorarioAtendimento
        fields = ['dia_semana', 'inicio', 'fim']
        labels = {'dia_semana': 'Dia da semana', 'inicio': 'Início', 'fim': 'Término'}
        widgets = {
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),
            'fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),
        }