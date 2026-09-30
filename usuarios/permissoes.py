def e_superuser(user):
    return user.is_superuser


def e_aluno(user):

    return hasattr(user, 'aluno')


def e_personal(user):
    return user.is_superuser or hasattr(user, 'personal')