from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.db import transaction
from django.db.models.aggregates import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from treinos.models import PlanoTreino, Exercicio
from usuarios.decorators import aluno_required, personal_required, superuser_required
from usuarios.forms import UsuarioForm, AlunoForm, LoginForm, PersonalForm
from usuarios.mixins import PersonalRequiredMixin, AlunoRequiredMixin
from usuarios.models import Aluno, Personal


# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'usuarios/acesso/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('usuarios:administrador_dashboard')
        if hasattr(user, 'aluno'):
            return reverse_lazy('usuarios:aluno_dashboard')
        elif hasattr(user, 'personal'):
            return reverse_lazy('usuarios:personal_dashboard')
        return reverse_lazy('web:home')

@superuser_required
def administrador_dashboard(request):
    return render(request, 'usuarios/admin/dashboard.html')

@aluno_required
def aluno_dashboard(request):
    return render(request, 'usuarios/aluno/dashboard.html')

class AlunoListView(PersonalRequiredMixin, ListView):
    model = Aluno
    template_name = 'usuarios/aluno/lista.html'
    context_object_name = 'alunos'

@personal_required
def criar_aluno(request):
    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        aluno_form = AlunoForm(request.POST)
        if user_form.is_valid() and aluno_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save()
                    aluno = aluno_form.save(commit=False)
                    aluno.user = user
                    aluno.save()
                messages.success(request,'Aluno cadastrado com sucesso!')
                return redirect('usuarios:aluno_lista')
            except Exception:
                messages.error(request,'Não foi possível cadastrar o aluno')

    else:
        user_form = UsuarioForm()
        aluno_form = AlunoForm()
    return render(request, 'usuarios/aluno/form.html',{
            'user_form' : user_form,
            'aluno_form' : aluno_form,
        })


@aluno_required
def aluno_editar_perfil(request):
    aluno = request.user.aluno  # já sabemos que é o próprio, sem precisar de pk

    if request.method == 'POST':
        aluno_form = AlunoForm(request.POST, instance=aluno)
        if aluno_form.is_valid():
            try:
                aluno_form.save()
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('usuarios:aluno_dashboard')
            except Exception:
                messages.error(request, 'Não foi possível editar seus dados')
    else:
        aluno_form = AlunoForm(instance=aluno)

    return render(request, 'usuarios/aluno/form.html',
                  {'aluno_form': aluno_form})


@personal_required
def editar_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        aluno_form = AlunoForm(request.POST, instance=aluno)
        if aluno_form.is_valid():
            try:
                aluno_form.save()
                messages.success(request,'Aluno editado com sucesso!')
                return redirect('usuarios:aluno_lista')
            except Exception:
                messages.error(request,'Não foi possível editar o aluno')
    else:
        aluno_form = AlunoForm(instance=aluno)
    return render(request, 'usuarios/aluno/form.html',
                  {'aluno_form': aluno_form})

class AlunoDetalhes(PersonalRequiredMixin , DetailView):
    model = Aluno
    template_name = 'usuarios/aluno/detalhe.html'
    context_object_name = 'aluno'

class AlunoMeuPerfil(AlunoRequiredMixin, DetailView):
    model = Aluno
    template_name = 'usuarios/aluno/detalhe.html'
    context_object_name = 'aluno'

    def get_object(self, queryset=None):
        return self.request.user.aluno

@personal_required
@require_POST
def excluir_aluno(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    user = aluno.user
    try:
        user.delete()
        messages.success(request,'Aluno excluído com sucesso!')
    except Exception:
        messages.error(request,'Não foi possível excluir o aluno')
    return redirect('usuarios:aluno_lista')

@personal_required
def personal_dashboard(request):
    hoje = timezone.now().date()
    limite = hoje + timedelta(days=15)

    # ---- Cards de métricas ----
    total_alunos = Aluno.objects.count()
    total_planos_ativos = PlanoTreino.objects.filter(status='A').count()
    total_exercicios = Exercicio.objects.count()

    # ---- Planos vencendo nos próximos 15 dias ----
    planos_vencendo = PlanoTreino.objects.filter(
        status='A',
        final__gte=hoje,
        final__lte=limite,
    ).select_related('aluno').order_by('final')

    # ---- Alunos sem plano ativo ----
    alunos_sem_plano = Aluno.objects.exclude(planos_treino__status='A')

    # ---- Planos agrupados por status ----
    contagem_por_status = PlanoTreino.objects.values('status').annotate(total=Count('id'))
    nomes_status = dict(PlanoTreino.STATUS_CHOICES)
    planos_por_status = [
        {
            'status_display': nomes_status.get(item['status'], item['status']),
            'total': item['total'],
        }
        for item in contagem_por_status
    ]

    contexto = {
        'total_alunos': total_alunos,
        'total_planos_ativos': total_planos_ativos,
        'total_exercicios': total_exercicios,
        'planos_vencendo': planos_vencendo,
        'total_planos_vencendo': planos_vencendo.count(),
        'alunos_sem_plano': alunos_sem_plano,
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
    personal = request.user.personal  # já sabemos que é o próprio, sem precisar de pk

    if request.method == 'POST':
        personal_form = PersonalForm(request.POST, instance=personal)
        if personal_form.is_valid():
            try:
                personal_form.save()
                messages.success(request, 'Dados atualizados com sucesso!')
                return redirect('usuarios:personal_dashboard')
            except Exception:
                messages.error(request, 'Não foi possível editar seus dados')
    else:
        personal_form = PersonalForm(instance=personal)

    return render(request, 'usuarios/personal/form.html',
                  {'personal_form': personal_form})


class PersonalListView(PersonalRequiredMixin, ListView):
    model = Personal
    template_name = 'usuarios/personal/lista.html'
    context_object_name = 'personals'


@personal_required
def criar_personal(request):
    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        personal_form = PersonalForm(request.POST)
        if user_form.is_valid() and personal_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save()
                    personal = personal_form.save(commit=False)
                    personal.user = user
                    personal.save()
                messages.success(request, 'Personal cadastrado com sucesso!')
                return redirect('usuarios:personal_lista')
            except Exception:
                messages.error(request, 'Não foi possível cadastrar o personal')
    else:
        user_form = UsuarioForm()
        personal_form = PersonalForm()
    return render(request, 'usuarios/personal/form.html', {
        'user_form': user_form,
        'personal_form': personal_form,
    })


@personal_required
def editar_personal(request, pk):
    personal = get_object_or_404(Personal, pk=pk)
    if request.method == 'POST':
        personal_form = PersonalForm(request.POST, instance=personal)
        if personal_form.is_valid():
            try:
                personal_form.save()
                messages.success(request, 'Personal editado com sucesso!')
                return redirect('usuarios:personal_lista')
            except Exception:
                messages.error(request, 'Não foi possível editar o personal')
    else:
        personal_form = PersonalForm(instance=personal)
    return render(request, 'usuarios/personal/form.html',
                  {'personal_form': personal_form})


class PersonalDetalhes(PersonalRequiredMixin, DetailView):
    model = Personal
    template_name = 'usuarios/personal/detalhe.html'
    context_object_name = 'personal'


@personal_required
@require_POST
def excluir_personal(request, pk):
    personal = get_object_or_404(Personal, pk=pk)
    user = personal.user
    try:
        user.delete()
        messages.success(request, 'Personal excluído com sucesso!')
    except Exception:
        messages.error(request, 'Não foi possível excluir o personal')
    return redirect('usuarios:personal_lista')

class MinhaPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'usuarios/acesso/alterar_senha.html'
    success_url = reverse_lazy('senha_alterada')


