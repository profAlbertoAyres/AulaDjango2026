from django.urls import path

from . import views

app_name = 'treinos'

urlpatterns = [
    # Exercício
    path('exercicios/', views.ExercicioListView.as_view(), name='exercicio_lista'),
    path('exercicios/novo/', views.ExercicioCreateView.as_view(), name='exercicio_novo'),
    path('exercicios/<int:pk>/', views.ExercicioDetailView.as_view(), name='exercicio_detalhe'),
    path('exercicios/<int:pk>/editar/', views.ExercicioUpdateView.as_view(), name='exercicio_editar'),
    path('exercicios/<int:pk>/excluir/', views.ExercicioDeleteView.as_view(), name='exercicio_excluir'),

    # Plano de Treino
    path('planos/', views.PlanoTreinoListView.as_view(), name='plano_lista'),
    path('planos/novo/', views.PlanoTreinoCreateView.as_view(), name='plano_novo'),
    path('planos/<int:pk>/', views.PlanoTreinoDetailView.as_view(), name='plano_detalhe'),
    path('planos/<int:pk>/editar/', views.PlanoTreinoUpdateView.as_view(), name='plano_editar'),
    path('planos/<int:pk>/excluir/', views.PlanoTreinoDeleteView.as_view(), name='plano_excluir'),

    # Sessão de Treino (função, sessão por vez)
    path('planos/<int:plano_pk>/sessoes/nova/', views.sessao_treino_form, name='sessao_nova'),
    path('planos/<int:plano_pk>/sessoes/<int:sessao_pk>/editar/', views.sessao_treino_form, name='sessao_editar'),
    path('planos/<int:plano_pk>/sessoes/<int:sessao_pk>/excluir/', views.sessao_treino_excluir, name='sessao_excluir'),
]