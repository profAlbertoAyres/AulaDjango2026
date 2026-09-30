from datetime import timedelta, datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView

from usuarios.mixins import PersonalRequiredMixin, AlunoRequiredMixin
from .forms import AgendaForm, RecusaForm, HorarioAtendimentoForm
from .models import Agenda, HorarioAtendimento, STATUS_ATIVOS, STATUS_QUE_OCUPAM

DURACAO_SLOT = 30


def agora_local():
    return timezone.localtime().replace(tzinfo=None)


def _converter(funcao, texto):
    try:
        return funcao(texto or '')
    except ValueError:
        return None


def data_da_requisicao(request):
    return _converter(parse_date, request.GET.get('data')) or timezone.localdate()


def gerar_horarios(data, periodos):
    duracao = timedelta(minutes=DURACAO_SLOT)
    horarios = []
    for periodo in periodos:
        if periodo.dia_semana != data.weekday():
            continue
        atual = datetime.combine(data, periodo.inicio)
        limite = datetime.combine(data, periodo.fim)
        while atual + duracao <= limite:
            horarios.append((atual.time(), (atual + duracao).time()))
            atual += duracao
    return horarios


def buscar_agendamento(agendamentos, data, hora):
    duracao = timedelta(minutes=DURACAO_SLOT)
    encontrados = []
    for ag in agendamentos:
        fim = ag.fim or (datetime.combine(data, ag.inicio) + duracao).time()
        if ag.inicio <= hora < fim:
            encontrados.append(ag)

    for ag in encontrados:
        if ag.status in STATUS_ATIVOS:
            return ag
    return encontrados[0] if encontrados else None


# Personal

class AgendaDiaView(PersonalRequiredMixin, TemplateView):
    template_name = 'agendas/agenda_dia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_selecionada = data_da_requisicao(self.request)

        agendamentos = list(
            Agenda.objects.filter(data=data_selecionada)
            .exclude(status__in=['CANCELADO', 'RECUSADO'])
            .select_related('aluno')
            .order_by('inicio')
        )
        periodos = list(HorarioAtendimento.objects.all())

        slots = []
        for inicio, fim in gerar_horarios(data_selecionada, periodos):
            slots.append({
                'inicio': inicio,
                'fim': fim,
                'agendamento': buscar_agendamento(agendamentos, data_selecionada, inicio),
            })

        context['data_selecionada'] = data_selecionada
        context['data_anterior'] = data_selecionada - timedelta(days=1)
        context['data_proxima'] = data_selecionada + timedelta(days=1)
        context['hoje'] = timezone.localdate()
        context['slots'] = slots
        return context


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
    template_name = 'agendas/form.html'

    def get_success_url(self):
        return f"{reverse('agendas:agenda_dia')}?data={self.object.data:%Y-%m-%d}"


class AgendaDeleteView(PersonalRequiredMixin, DeleteView):
    model = Agenda
    template_name = 'agendas/agenda_confirm_delete.html'
    def get_success_url(self):
        # volta para o dia do agendamento excluído, e não para "hoje"
        return f"{reverse('agendas:agenda_dia')}?data={self.object.data:%Y-%m-%d}"

    def form_valid(self, form):
        messages.success(self.request, 'Agendamento excluído.')
        return super().form_valid(form)


class AgendaConfirmarView(PersonalRequiredMixin, View):

    def post(self, request, pk):
        agendamento = get_object_or_404(Agenda, pk=pk, status='AGENDADO')
        agendamento.status = 'REALIZADO'
        agendamento.save(update_fields=['status'])
        return redirect(f"{reverse('agendas:agenda_dia')}?data={agendamento.data:%Y-%m-%d}")


class AgendaCancelarView(PersonalRequiredMixin, View):

    def post(self, request, pk):
        agendamento = get_object_or_404(Agenda, pk=pk, status__in=['AGENDADO', 'BLOQUEADO'])
        agendamento.status = 'CANCELADO'
        agendamento.save(update_fields=['status'])
        return redirect(f"{reverse('agendas:agenda_dia')}?data={agendamento.data:%Y-%m-%d}")


class AgendaAceitarView(PersonalRequiredMixin, View):

    def post(self, request, pk):
        agendamento = get_object_or_404(Agenda, pk=pk, status='SOLICITADO')
        agendamento.status = 'AGENDADO'
        agendamento.save(update_fields=['status'])
        return redirect(f"{reverse('agendas:agenda_dia')}?data={agendamento.data:%Y-%m-%d}")


class AgendaRecusarView(PersonalRequiredMixin, UpdateView):
    model = Agenda
    form_class = RecusaForm
    template_name = 'agendas/agenda_recusar.html'
    queryset = Agenda.objects.filter(status='SOLICITADO')  # só recusa quem está pendente

    def form_valid(self, form):
        form.instance.status = 'RECUSADO'
        return super().form_valid(form)

    def get_success_url(self):
        return f"{reverse('agendas:agenda_dia')}?data={self.object.data:%Y-%m-%d}"


# Aluno

class AgendaSemanaAlunoView(AlunoRequiredMixin, TemplateView):
    template_name = 'agendas/agenda_semana_aluno.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno = self.request.user.aluno
        data_selecionada = data_da_requisicao(self.request)

        inicio_semana = data_selecionada - timedelta(days=data_selecionada.weekday())
        dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]

        agendamentos = list(
            Agenda.objects.filter(data__range=[dias_semana[0], dias_semana[-1]])
            .exclude(status='CANCELADO')
        )
        periodos = list(HorarioAtendimento.objects.all())

        dias = []
        for dia in dias_semana:
            agendamentos_do_dia = [a for a in agendamentos if a.data == dia]
            slots = []
            for inicio, fim in gerar_horarios(dia, periodos):
                ag = buscar_agendamento(agendamentos_do_dia, dia, inicio)
                slots.append(self._resolver_slot(dia, inicio, fim, ag, aluno))
            if slots:
                dias.append({'data': dia, 'slots': slots})

        context['dias_semana'] = dias_semana
        context['dias'] = dias
        context['semana_anterior'] = inicio_semana - timedelta(days=7)
        context['semana_proxima'] = inicio_semana + timedelta(days=7)
        context['hoje'] = timezone.localdate()
        return context

    def _resolver_slot(self, data, inicio, fim, ag, aluno):

        base = {'data': data, 'inicio': inicio, 'fim': fim,
                'agendamento_id': None, 'justificativa': None}

        if ag is None:
            return {**base, 'estado': 'livre'}

        if ag.status == 'BLOQUEADO':
            return {**base, 'estado': 'bloqueado'}

        e_meu = ag.aluno_id == aluno.id

        if ag.status not in STATUS_QUE_OCUPAM:
            if e_meu and ag.status == 'RECUSADO':
                return {
                    **base,
                    'estado': 'meu_recusado',
                    'agendamento_id': ag.id,
                    'justificativa': ag.justificativa,
                }
            return {**base, 'estado': 'livre'}

        if not e_meu:
            return {**base, 'estado': 'ocupado'}

        if ag.status == 'SOLICITADO':
            estado = 'meu_solicitado'
        elif ag.status == 'AGENDADO':
            estado = 'meu_confirmado'
        else:  # REALIZADO
            estado = 'meu_realizado'

        return {**base, 'estado': estado, 'agendamento_id': ag.id}


class AgendaSolicitarView(AlunoRequiredMixin, View):

    def post(self, request):
        aluno = request.user.aluno
        data = _converter(parse_date, request.POST.get('data'))
        inicio = _converter(parse_time, request.POST.get('inicio'))
        fim = _converter(parse_time, request.POST.get('fim'))

        if not (data and inicio and fim):
            messages.error(request, 'Horário inválido.')
            return redirect('agendas:agenda_semana_aluno')

        destino = f"{reverse('agendas:agenda_semana_aluno')}?data={data:%Y-%m-%d}"

        # 1. não pode ser um horário que já passou
        if datetime.combine(data, inicio) < agora_local():
            messages.error(request, 'Não é possível solicitar um horário que já passou.')
            return redirect(destino)

        # 2. precisa ser um horário dentro do atendimento do personal
        periodos = list(HorarioAtendimento.objects.all())
        if (inicio, fim) not in gerar_horarios(data, periodos):
            messages.error(request, 'Esse horário está fora do atendimento do personal.')
            return redirect(destino)

        ativos = Agenda.objects.filter(data=data, status__in=STATUS_ATIVOS)
        if buscar_agendamento(ativos, data, inicio):
            messages.error(request, 'Esse horário acabou de ser ocupado. Escolha outro.')
            return redirect(destino)

        try:
            with transaction.atomic():
                Agenda.objects.create(
                    aluno=aluno,
                    data=data,
                    inicio=inicio,
                    fim=fim,
                    status='SOLICITADO',
                )
        except (ValidationError, IntegrityError):
            messages.error(request, 'Esse horário acabou de ser ocupado. Escolha outro.')
            return redirect(destino)

        messages.success(request, 'Solicitação enviada! Aguarde a confirmação do personal.')
        return redirect(destino)

class AgendaCancelarMeuView(AlunoRequiredMixin, View):

    def post(self, request, pk):
        agendamento = get_object_or_404(
            Agenda, pk=pk, aluno=request.user.aluno, status__in=['SOLICITADO', 'AGENDADO']
        )
        agendamento.status = 'CANCELADO'
        agendamento.save(update_fields=['status'])
        return redirect(f"{reverse('agendas:agenda_semana_aluno')}?data={agendamento.data:%Y-%m-%d}")


class HorarioAtendimentoView(PersonalRequiredMixin, CreateView):
    model = HorarioAtendimento
    form_class = HorarioAtendimentoForm
    template_name = 'agendas/horarios.html'
    success_url = reverse_lazy('agendas:horarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        periodos = list(HorarioAtendimento.objects.all())
        context['dias'] = [
            {'nome': nome, 'periodos': [p for p in periodos if p.dia_semana == numero]}
            for numero, nome in HorarioAtendimento.DIAS
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Período cadastrado.')
        return super().form_valid(form)


class HorarioAtendimentoExcluirView(PersonalRequiredMixin, View):

    def post(self, request, pk):
        periodo = get_object_or_404(HorarioAtendimento, pk=pk)

        futuros = Agenda.objects.filter(
            data__gte=timezone.localdate(),
            status__in=['SOLICITADO', 'AGENDADO'],
            inicio__gte=periodo.inicio,
            inicio__lt=periodo.fim,
        )
        if any(ag.data.weekday() == periodo.dia_semana for ag in futuros):
            messages.error(
                request,
                'Há solicitações ou agendamentos futuros nesse período. Cancele-os antes de remover.'
            )
        else:
            periodo.delete()
            messages.success(request, 'Período removido.')
        return redirect('agendas:horarios')