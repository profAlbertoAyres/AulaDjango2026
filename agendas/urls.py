from django.urls import path

from agendas.views import AgendaCreateView, AgendaUpdateView, AgendaDeleteView, AgendaDiaView, AgendaConfirmarView, \
    AgendaCancelarView

app_name = 'agendas'

urlpatterns = [
    path('', AgendaDiaView.as_view(), name='agenda_dia'),
    path('novo/', AgendaCreateView.as_view(), name='agenda_novo'),
    path('<int:pk>/editar/', AgendaUpdateView.as_view(), name='agenda_editar'),
    path('<int:pk>/excluir/', AgendaDeleteView.as_view(), name='agenda_excluir'),
    path('<int:pk>/confirmar/', AgendaConfirmarView.as_view(), name='agenda_confirmar'),
    path('<int:pk>/cancelar/', AgendaCancelarView.as_view(), name='agenda_cancelar'),
]