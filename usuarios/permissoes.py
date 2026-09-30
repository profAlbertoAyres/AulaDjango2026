def e_superuser(user):
    return user.is_superuser


def e_aluno(user):
    # Só quem tem perfil de aluno. O superusuário NÃO passa aqui,
    # porque as telas do aluno dependem de request.user.aluno.
    return hasattr(user, 'aluno')


def e_personal(user):
    # O superusuário passa (administra o sistema todo).
    return user.is_superuser or hasattr(user, 'personal')