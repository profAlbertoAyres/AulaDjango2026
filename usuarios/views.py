from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.db import DatabaseError, transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from agendas.models import Agenda
from treinos.models import PlanoTreino, Exercicio
from usuarios.decorators import aluno_required, personal_required, superuser_required
from usuarios.forms import UsuarioForm, AlunoForm, LoginForm, PersonalForm
from usuarios.mixins import PersonalRequiredMixin, AlunoRequiredMixin, SuperuserRequiredMixin
from usuarios.models import Aluno, Personal

DIAS_ALERTA_VENCIMENTO = 15
DIAS_RECUSAS_RECENTES = 7


def _salvar_usuario_e_perfil(user_form, perfil_form):
    with transaction.atomic():
        user = user_form.save()
        perfil = perfil_form.save(commit=False)
        perfil.user = user
        perfil.save()
    return perfil


class CustomLoginView(LoginView):
    template_name = 'usuarios/acesso/login.html'
    authentication_form = LoginForm

    def get_default_redirect_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('usuarios:administrador_dashboard')
        if hasattr(user, 'aluno'):
            return reverse_lazy('usuarios:aluno_dashboard')
        if hasattr(user, 'personal'):
            return reverse_lazy('usuarios:personal_dashboard')
        return reverse_lazy('web:home')


class MinhaPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'usuarios/acesso/alterar_senha.html'
    success_url = reverse_lazy('senha_alterada')


@superuser_required
def administrador_dashboard(request):
    return render(request, 'usuarios/admin/dashboard.html')


class PersonalListView(SuperuserRequiredMixin, ListView):
    model = Personal
    template_name = 'usuarios/personal/lista.html'
    context_object_name = 'personals'


class PersonalDetalhes(SuperuserRequiredMixin, DetailView):
    model = Personal
    template_name = 'usuarios/personal/detalhe.html'
    context_object_name = 'personal'


@superuser_required
def criar_personal(request):
    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        personal_form = PersonalForm(request.POST)
        if user_form.is_valid() and personal_form.is_valid():
            try:
                _salvar_usuario_e_perfil(user_form, personal_form)
                messages.success(request, 'Personal cadastrado com sucesso!')
                return redirect('usuarios:personal_lista')
            except DatabaseError:
                messages.error(request, 'Não foi possível cadastrar o personal')
    else:
        user_form = UsuarioForm()
        personal_form = PersonalForm()

    return render(request, 'usuarios/personal/form.html', {
        'user_form': user_form,
        'personal_form': personal_form,
    })


@superuser_required
def editar_personal(request, pk):
    personal = get_object_or_404(Personal, pk=pk)
    if request.method == 'POST':
        personal_form = PersonalForm(request.POST, instance=personal)
        if personal_form.is_valid():
            try:
                personal_form.save()
                messages.success(request, 'Personal editado com sucesso!')
                return redirect('usuarios:personal_lista')
            except DatabaseError:
                messages.error(request, 'Não foi possível editar o personal')
    else:
        personal_form = PersonalForm(instance=personal)

    return render(request, 'usuarios/personal/form.html', {'personal_form': personal_form})


@superuser_required
@require_POST
def excluir_personal(request, pk):
    personal = get_object_or_404(Personal, pk=pk)
    try:
        personal.user.delete()
        messages.success(request, 'Personal excluído com sucesso!')
    except DatabaseError:
        messages.error(request, 'Não foi possível excluir o personal')
    return redirect('usuarios:personal_lista')


@personal_required
def personal_dashboard(request):
    hoje = timezone.localdate()
    limite = hoje + timedelta(days=DIAS_ALERTA_VENCIMENTO)

    planos_vencendo = (
        PlanoTreino.objects
        .filter(status='A', final__gte=hoje, final__lte=limite)
        .select_related('aluno')
        .order_by('final')
    )

    nomes_status = dict(PlanoTreino.STATUS_CHOICES)
    planos_por_status = [
        {
            'status_display': nomes_status.get(item['status'], item['status']),
            'total': item['total'],
        }
        for item in PlanoTreino.objects.values('status').annotate(total=Count('id'))
    ]

    contexto = {
        'total_alunos': Aluno.objects.count(),
        'total_planos_ativos': PlanoTreino.objects.filter(status='A').count(),
        'total_exercicios': Exercicio.objects.count(),
        'planos_vencendo': planos_vencendo,
        'total_planos_vencendo': planos_vencendo.count(),
        'alunos_sem_plano': Aluno.objects.exclude(planos_treino__status='A'),
        'planos_por_status': planos_por_status,
    }
    return render(request, 'usuarios/personal/dashboard.html', contexto)


class PersonalMeuPerfil(PersonalRequiredMixin, DetailView):
    model = Personal
    template_name = 'usuarios/personal/detalhe.html'
    context_object_name = 'personal'

    def get_object(self, queryset=None):
        return self.request.user.personal


@personal_required
def personal_editar_perfil(request):
    personal = request.user.personal

    if request.method == 'POST':
        personal_form = PersonalForm(request.POST, instance=personal)
        if personal_form.is_valid():
            try:
                personal_form.save()
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('usuarios:personal_dashboard')
            except DatabaseError:
                messages.error(request, 'Não foi possível editar seus dados')
    else:
        personal_form = PersonalForm(instance=personal)

    return render(request, 'usuarios/personal/form.html', {'personal_form': personal_form})


class AlunoListView(PersonalRequiredMixin, ListView):
    model = Aluno
    template_name = 'usuarios/aluno/lista.html'
    context_object_name = 'alunos'


class AlunoDetalhes(PersonalRequiredMixin, DetailView):
    model = Aluno
    template_name = 'usuarios/aluno/detalhe.html'
    context_object_name = 'aluno'


@personal_required
def criar_aluno(request):
    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        aluno_form = AlunoForm(request.POST)
        if user_form.is_valid() and aluno_form.is_valid():
            try:
                _salvar_usuario_e_perfil(user_form, aluno_form)
                messages.success(request, 'Aluno cadastrado com sucesso!')
                return redirect('usuarios:aluno_lista')
            except DatabaseError:
                messages.error(request, 'Não foi possível cadastrar o aluno')
    else:
        user_form = UsuarioForm()
        aluno_form = AlunoForm()

    return render(request, 'usuarios/aluno/form.html', {
        'user_form': user_form,
        'aluno_form': aluno_form,
    })


@personal_required
def editar_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        aluno_form = AlunoForm(request.POST, instance=aluno)
        if aluno_form.is_valid():
            try:
                aluno_form.save()
                messages.success(request, 'Aluno editado com sucesso!')
                return redirect('usuarios:aluno_lista')
            except DatabaseError:
                messages.error(request, 'Não foi possível editar o aluno')
    else:
        aluno_form = AlunoForm(instance=aluno)

    return render(request, 'usuarios/aluno/form.html', {'aluno_form': aluno_form})


@personal_required
@require_POST
def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    try:
        aluno.user.delete()
        messages.success(request, 'Aluno excluído com sucesso!')
    except DatabaseError:
        messages.error(request, 'Não foi possível excluir o aluno')
    return redirect('usuarios:aluno_lista')


class AlunoMeuPerfil(AlunoRequiredMixin, DetailView):
    model = Aluno
    template_name = 'usuarios/aluno/detalhe.html'
    context_object_name = 'aluno'

    def get_object(self, queryset=None):
        return self.request.user.aluno


@aluno_required
def aluno_editar_perfil(request):
    aluno = request.user.aluno

    if request.method == 'POST':
        aluno_form = AlunoForm(request.POST, instance=aluno)
        if aluno_form.is_valid():
            try:
                aluno_form.save()
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('usuarios:aluno_dashboard')
            except DatabaseError:
                messages.error(request, 'Não foi possível editar seus dados')
    else:
        aluno_form = AlunoForm(instance=aluno)

    return render(request, 'usuarios/aluno/form.html', {'aluno_form': aluno_form})


@aluno_required
def aluno_dashboard(request):
    aluno = request.user.aluno
    hoje = timezone.localdate()
    limite_vencimento = hoje + timedelta(days=DIAS_ALERTA_VENCIMENTO)

    plano_ativo = (
        aluno.planos_treino
        .filter(status='A')
        .prefetch_related('sessoes__exercicios_da_sessao')
        .order_by('-inicio')
        .first()
    )

    dias_restantes = None
    plano_vencendo = False
    sessoes_resumo = []

    if plano_ativo:
        if plano_ativo.final:
            dias_restantes = (plano_ativo.final - hoje).days
            plano_vencendo = hoje <= plano_ativo.final <= limite_vencimento

        sessoes_resumo = [
            {
                'nome': sessao.nome,
                'total_exercicios': len(sessao.exercicios_da_sessao.all()),
            }
            for sessao in plano_ativo.sessoes.all()
        ]

    agendamentos_futuros = Agenda.objects.filter(aluno=aluno, data__gte=hoje)

    proximos_agendamentos = (
        agendamentos_futuros
        .filter(status__in=['SOLICITADO', 'AGENDADO'])
        .order_by('data', 'inicio')[:5]
    )

    proximo_confirmado = (
        agendamentos_futuros
        .filter(status='AGENDADO')
        .order_by('data', 'inicio')
        .first()
    )

    recusas_recentes = (
        Agenda.objects
        .filter(
            aluno=aluno,
            status='RECUSADO',
            data__gte=hoje - timedelta(days=DIAS_RECUSAS_RECENTES),
        )
        .order_by('-data')
    )

    contexto = {
        'plano_ativo': plano_ativo,
        'dias_restantes': dias_restantes,
        'plano_vencendo': plano_vencendo,
        'sessoes_resumo': sessoes_resumo,
        'total_sessoes': len(sessoes_resumo),
        'proximo_confirmado': proximo_confirmado,
        'proximos_agendamentos': proximos_agendamentos,
        'recusas_recentes': recusas_recentes,
    }
    return render(request, 'usuarios/aluno/dashboard.html', contexto)