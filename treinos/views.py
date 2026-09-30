from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView

from usuarios.decorators import personal_required
from usuarios.mixins import PersonalRequiredMixin, AlunoRequiredMixin
from .models import Exercicio, PlanoTreino, SessaoTreino
from .forms import ExercicioForm, PlanoTreinoForm, SessaoTreinoForm, SessaoExercicioFormSet, FotoExercicioFormSet


# ---------- Exercício ----------

class ExercicioFormsetMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'fotos_formset' not in context:
            context['fotos_formset'] = FotoExercicioFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        fotos_formset = FotoExercicioFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object,
        )

        if not fotos_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, fotos_formset=fotos_formset)
            )

        with transaction.atomic():
            self.object.save()
            form.save_m2m()
            fotos_formset.instance = self.object
            fotos_formset.save()

        return redirect(self.get_success_url())

class ExercicioListView(PersonalRequiredMixin, ListView):
    model = Exercicio
    template_name = 'treinos/exercicio/lista.html'
    context_object_name = 'exercicios'


class ExercicioDetailView(PersonalRequiredMixin, DetailView):
    model = Exercicio
    template_name = 'treinos/exercicio/detalhe.html'
    context_object_name = 'exercicio'


class ExercicioCreateView(PersonalRequiredMixin, ExercicioFormsetMixin, CreateView):
    model = Exercicio
    form_class = ExercicioForm
    template_name = 'treinos/exercicio/form.html'
    success_url = reverse_lazy('treinos:exercicio_lista')


class ExercicioUpdateView(PersonalRequiredMixin, ExercicioFormsetMixin, UpdateView):
    model = Exercicio
    form_class = ExercicioForm
    template_name = 'treinos/exercicio/form.html'
    success_url = reverse_lazy('treinos:exercicio_lista')


class ExercicioDeleteView(PersonalRequiredMixin, DeleteView):
    model = Exercicio
    http_method_names = ['post']
    success_url = reverse_lazy('treinos:exercicio_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Exercício excluído com sucesso.')
        return super().form_valid(form)


# ---------- Plano de Treino ----------

class PlanoTreinoListView(PersonalRequiredMixin, ListView):
    model = PlanoTreino
    template_name = 'treinos/plano/lista.html'
    context_object_name = 'planos'

# Tela 1: cadastro do plano
class PlanoTreinoCreateView(PersonalRequiredMixin, CreateView):
    model = PlanoTreino
    form_class = PlanoTreinoForm
    template_name = 'treinos/plano/form.html'

    def get_success_url(self):
        return reverse_lazy('treinos:plano_detalhe', kwargs={'pk': self.object.pk})


class PlanoTreinoDetailView(PersonalRequiredMixin, DetailView):
    model = PlanoTreino
    template_name = 'treinos/plano/detalhe.html'
    context_object_name = 'plano'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessoes'] = self.object.sessoes.prefetch_related('exercicios_da_sessao__exercicio')
        return context


class PlanoTreinoUpdateView(PersonalRequiredMixin, UpdateView):
    model = PlanoTreino
    form_class = PlanoTreinoForm
    template_name = 'treinos/plano/form.html'

    def get_success_url(self):
        return reverse_lazy('treinos:plano_detalhe', kwargs={'pk': self.object.pk})


class PlanoTreinoDeleteView(PersonalRequiredMixin, DeleteView):
    model = PlanoTreino
    template_name = 'treinos/plano/plano_confirm_delete.html'
    success_url = reverse_lazy('treinos:plano_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Plano de treino excluído com sucesso.')
        return super().form_valid(form)


# ---------- Sessão de Treino (Tela 3: form da sessão + formset de exercícios) ----------

@personal_required
def sessao_treino_form(request, plano_pk, sessao_pk=None):
    plano = get_object_or_404(PlanoTreino, pk=plano_pk)

    if sessao_pk:
        # editar sessão existente
        sessao = get_object_or_404(SessaoTreino, pk=sessao_pk, plano_treino=plano)
    else:
        # nova sessão (ainda não salva no banco)
        sessao = SessaoTreino(plano_treino=plano)

    if request.method == 'POST':
        form = SessaoTreinoForm(request.POST, instance=sessao)
        formset = SessaoExercicioFormSet(request.POST, instance=sessao)

        if form.is_valid() and formset.is_valid():
            sessao = form.save(commit=False)
            sessao.plano_treino = plano
            sessao.save()

            formset.instance = sessao  # garante o vínculo com a sessão salva
            formset.save()

            messages.success(request, 'Sessão salva com sucesso!')
            return redirect('treinos:plano_detalhe', pk=plano.pk)
    else:
        form = SessaoTreinoForm(instance=sessao)
        formset = SessaoExercicioFormSet(instance=sessao)

    contexto = {
        'plano': plano,
        'form': form,
        'formset': formset,
    }
    return render(request, 'treinos/plano/sessao_form.html', contexto)


@personal_required
@require_POST
def sessao_treino_excluir(request, plano_pk, sessao_pk):
    sessao = get_object_or_404(SessaoTreino, pk=sessao_pk, plano_treino_id=plano_pk)
    sessao.delete()
    messages.success(request, 'Sessão excluída com sucesso.')
    return redirect('treinos:plano_detalhe', pk=plano_pk)


class MeuTreinoView(AlunoRequiredMixin, TemplateView):
    """Treino completo do aluno logado (plano ativo, com sessões e exercícios)."""
    template_name = 'treinos/aluno/meu_treino.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plano'] = (
            self.request.user.aluno.planos_treino
            .filter(status='A')
            .prefetch_related('sessoes__exercicios_da_sessao__exercicio__fotos')
            .order_by('-inicio')
            .first()
        )
        return context