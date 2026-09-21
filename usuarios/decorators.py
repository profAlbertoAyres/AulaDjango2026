from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def superuser_required(view_func):
    @wraps(view_func)
    @login_required
    def view_protegida(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return view_protegida


def aluno_required(view_func):
    @wraps(view_func)
    @login_required
    def view_protegida(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if not hasattr(request.user, 'aluno'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return view_protegida

def personal_required(view_func):
    @wraps(view_func)
    @login_required
    def view_protegida(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if not hasattr(request.user, 'personal'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return view_protegida