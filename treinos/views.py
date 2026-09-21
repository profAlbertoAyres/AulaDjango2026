from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from usuarios.mixins import PersonalRequiredMixin
from .models import Exercicio, PlanoTreino, SessaoTreino
from .forms import ExercicioForm, PlanoTreinoForm, SessaoTreinoForm, SessaoExercicioFormSet


# ---------- Exercício ----------

class ExercicioListView(PersonalRequiredMixin, ListView):
    model = Exercicio
    template_name = 'treinos/exercicio/lista.html'
    context_object_name = 'exercicios'


class ExercicioDetailView(PersonalRequiredMixin, DetailView):
    model = Exercicio
    template_name = 'treinos/exercicio/detalhe.html'
    context_object_name = 'exercicio'


class ExercicioCreateView(PersonalRequiredMixin, CreateView):
    model = Exercicio
    form_class = ExercicioForm
    template_name = 'treinos/exercicio/form.html'
    success_url = reverse_lazy('treinos:exercicio_lista')


class ExercicioUpdateView(PersonalRequiredMixin, UpdateView):
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


# ---------- Sessão de Treino (Tela 3: form da sessão + formset de exercícios) ----------

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


def sessao_treino_excluir(request, plano_pk, sessao_pk):
    sessao = get_object_or_404(SessaoTreino, pk=sessao_pk, plano_treino_id=plano_pk)
    sessao.delete()
    messages.success(request, 'Sessão excluída com sucesso.')
    return redirect('treinos:plano_detalhe', pk=plano_pk)