from datetime import date, timedelta, datetime

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView

from usuarios.mixins import PersonalRequiredMixin
from .models import Agenda
from .forms import AgendaForm


HORA_INICIO = 8    # 08:00
HORA_FIM = 18       # 18:00
DURACAO_SLOT = 30   # minutos


class AgendaDiaView(PersonalRequiredMixin, TemplateView):
    template_name = 'agendas/agenda_dia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data_str = self.request.GET.get('data')
        data_selecionada = parse_date(data_str) if data_str else date.today()
        if data_selecionada is None:
            data_selecionada = date.today()

        agendamentos = list(
            Agenda.objects.filter(data=data_selecionada)
            .exclude(status='CANCELADO')
            .select_related('aluno')
            .order_by('inicio')
        )

        context['data_selecionada'] = data_selecionada
        context['data_anterior'] = data_selecionada - timedelta(days=1)
        context['data_proxima'] = data_selecionada + timedelta(days=1)
        context['hoje'] = date.today()
        context['slots'] = self._montar_slots(agendamentos, data_selecionada)
        return context

    def _montar_slots(self, agendamentos, data_selecionada):
        slots = []
        atual = datetime.combine(data_selecionada, datetime.min.time()).replace(hour=HORA_INICIO)
        limite = datetime.combine(data_selecionada, datetime.min.time()).replace(hour=HORA_FIM)

        while atual < limite:
            proximo = atual + timedelta(minutes=DURACAO_SLOT)
            hora_atual = atual.time()

            agendamento_encontrado = None
            for ag in agendamentos:
                fim_ag = ag.fim or (
                    (datetime.combine(data_selecionada, ag.inicio) + timedelta(minutes=DURACAO_SLOT)).time()
                )
                if ag.inicio <= hora_atual < fim_ag:
                    agendamento_encontrado = ag
                    break

            slots.append({
                'inicio': hora_atual,
                'fim': proximo.time(),
                'agendamento': agendamento_encontrado,
                'ocupado': agendamento_encontrado is not None,
            })
            atual = proximo

        return slots


class AgendaCreateView(PersonalRequiredMixin, CreateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'agendas/form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['data'] = self.request.GET.get('data')
        initial['inicio'] = self.request.GET.get('inicio')
        initial['fim'] = self.request.GET.get('fim')
        return initial

    def get_success_url(self):
        return f"{reverse('agendas:agenda_dia')}?data={self.object.data:%Y-%m-%d}"


class AgendaUpdateView(PersonalRequiredMixin, UpdateView):
    model = Agenda
    form_class = AgendaForm
    template_name = 'agendas/agenda_form.html'

    def get_success_url(self):
        return f"{reverse('agendas:agenda_dia')}?data={self.object.data:%Y-%m-%d}"


class AgendaDeleteView(PersonalRequiredMixin, DeleteView):
    model = Agenda
    template_name = 'agendas/agenda_confirm_delete.html'
    success_url = reverse_lazy('agendas:agenda_dia')


class AgendaConfirmarView(PersonalRequiredMixin, View):
    """Marca o agendamento como REALIZADO."""

    def post(self, request, pk):
        agendamento = get_object_or_404(Agenda, pk=pk)
        agendamento.status = 'REALIZADO'
        agendamento.save(update_fields=['status'])
        return redirect(f"{reverse('agendas:agenda_dia')}?data={agendamento.data:%Y-%m-%d}")


class AgendaCancelarView(PersonalRequiredMixin,View):
    """Marca o agendamento como CANCELADO (libera o horário)."""

    def post(self, request, pk):
        agendamento = get_object_or_404(Agenda, pk=pk)
        agendamento.status = 'CANCELADO'
        agendamento.save(update_fields=['status'])
        return redirect(f"{reverse('agendas:agenda_dia')}?data={agendamento.data:%Y-%m-%d}")