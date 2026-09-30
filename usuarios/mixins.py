from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .permissoes import e_aluno, e_personal, e_superuser


class PerfilRequiredMixin(LoginRequiredMixin):
    mensagem_negado = 'Você não tem permissão para acessar esta área.'

    def tem_permissao(self, user):
        raise NotImplementedError('Defina tem_permissao() na subclasse.')

    def dispatch(self, request, *args, **kwargs):
        # Anônimo: o LoginRequiredMixin (no super) redireciona para o login.
        if request.user.is_authenticated and not self.tem_permissao(request.user):
            raise PermissionDenied(self.mensagem_negado)
        return super().dispatch(request, *args, **kwargs)


class AlunoRequiredMixin(PerfilRequiredMixin):
    mensagem_negado = 'Esta área é exclusiva para alunos.'

    def tem_permissao(self, user):
        return e_aluno(user)


class PersonalRequiredMixin(PerfilRequiredMixin):
    mensagem_negado = 'Esta área é exclusiva para personais.'

    def tem_permissao(self, user):
        return e_personal(user)


class SuperuserRequiredMixin(PerfilRequiredMixin):
    mensagem_negado = 'Esta área é exclusiva para administradores.'

    def tem_permissao(self, user):
        return e_superuser(user)