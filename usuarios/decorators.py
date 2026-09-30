from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .permissoes import e_aluno, e_personal, e_superuser


def _perfil_required(tem_permissao, mensagem):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def view_protegida(request, *args, **kwargs):
            if not tem_permissao(request.user):
                raise PermissionDenied(mensagem)
            return view_func(request, *args, **kwargs)
        return view_protegida
    return decorator


superuser_required = _perfil_required(e_superuser, 'Esta área é exclusiva para administradores.')
aluno_required = _perfil_required(e_aluno, 'Esta área é exclusiva para alunos.')
personal_required = _perfil_required(e_personal, 'Esta área é exclusiva para personais.')