from django.urls import path

from agendas.views import AgendaCreateView, AgendaUpdateView, AgendaDeleteView, AgendaDiaView, AgendaConfirmarView, \
    AgendaCancelarView, AgendaSemanaAlunoView, AgendaSolicitarView, AgendaCancelarMeuView, AgendaAceitarView, \
    AgendaRecusarView, HorarioAtendimentoView, HorarioAtendimentoExcluirView

app_name = 'agendas'

urlpatterns = [
    path('', AgendaDiaView.as_view(), name='agenda_dia'),
    path('novo/', AgendaCreateView.as_view(), name='agenda_novo'),
    path('<int:pk>/editar/', AgendaUpdateView.as_view(), name='agenda_editar'),
    path('<int:pk>/excluir/', AgendaDeleteView.as_view(), name='agenda_excluir'),
    path('<int:pk>/confirmar/', AgendaConfirmarView.as_view(), name='agenda_confirmar'),
    path('<int:pk>/cancelar/', AgendaCancelarView.as_view(), name='agenda_cancelar'),
    path('minha-semana/', AgendaSemanaAlunoView.as_view(), name='agenda_semana_aluno'),
    path('solicitar/', AgendaSolicitarView.as_view(), name='agenda_solicitar'),
    path('<int:pk>/cancelar-meu/', AgendaCancelarMeuView.as_view(), name='agenda_cancelar_meu'),
    path('<int:pk>/aceitar/', AgendaAceitarView.as_view(), name='agenda_aceitar'),
    path('<int:pk>/recusar/', AgendaRecusarView.as_view(), name='agenda_recusar'),
    path('horarios/', HorarioAtendimentoView.as_view(), name='horarios'),
    path('horarios/<int:pk>/excluir/', HorarioAtendimentoExcluirView.as_view(), name='horario_excluir'),
]