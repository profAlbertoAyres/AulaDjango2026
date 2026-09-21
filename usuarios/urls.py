from django.urls import path

from . import views

app_name = 'usuarios'

urlpatterns = [
    #Admin
    path('administrador/',views.administrador_dashboard, name='administrador_dashboard'),
    # Aluno
    path('alunos/', views.aluno_dashboard, name='aluno_dashboard'),
    path('alunos/lista/', views.AlunoListView.as_view(), name='aluno_lista'),
    path('alunos/novo/', views.criar_aluno, name='aluno_novo'),
    path('alunos/<int:pk>/editar', views.editar_aluno, name='aluno_editar'),
    path('aluno/<int:pk>', views.AlunoDetalhes.as_view(), name='aluno_detalhe'),
    path('alunos/<int:pk>/excluir', views.excluir_aluno, name='aluno_excluir'),
    path('aluno/perfil/editar/', views.aluno_editar_perfil, name='aluno_editar_perfil'),
    path('aluno/meu-perfil/', views.AlunoMeuPerfil.as_view(), name='aluno_meu_perfil'),

    # Personal
    path('personal/', views.personal_dashboard, name='personal_dashboard'),
    path('personal/meu-perfil/', views.PersonalMeuPerfil.as_view(), name='personal_meu_perfil'),
    path('personal/perfil/editar/', views.personal_editar_perfil, name='personal_editar_perfil'),
    path('personals/lista/', views.PersonalListView.as_view(), name='personal_lista'),
    path('personals/novo/', views.criar_personal, name='personal_novo'),
    path('personals/<int:pk>/editar', views.editar_personal, name='personal_editar'),
    path('personal/<int:pk>', views.PersonalDetalhes.as_view(), name='personal_detalhe'),
    path('personals/<int:pk>/excluir', views.excluir_personal, name='personal_excluir'),
]