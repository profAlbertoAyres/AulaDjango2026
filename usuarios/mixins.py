from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class AlunoRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)  # LoginRequiredMixin cuida do redirect

        if request.user.is_superuser or hasattr(request.user, 'aluno'):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied('Esta área é exclusiva para alunos.')


class PersonalRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if request.user.is_superuser or hasattr(request.user, 'personal'):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied('Esta área é exclusiva para personais.')