"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include, reverse_lazy

from usuarios import views
from usuarios.forms import LoginForm, PasswordResetForm, MinhaPasswordChangeForm, ResetPasswordForm, \
    MinhaSetPasswordForm
from usuarios.views import MinhaPasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('agenda/', include('agendas.urls')),
    path('treinos/', include('treinos.urls')),

    # Acessos
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('senha/alterar/', MinhaPasswordChangeView.as_view(form_class=MinhaPasswordChangeForm), name='alterar_senha'),

    path('senha/alterada/', PasswordChangeDoneView.as_view(template_name='usuarios/acesso/senha_alterada.html'),
         name='senha_alterada'),

    path('senha/resetar/', PasswordResetView.as_view(
        template_name='usuarios/acesso/esqueci_senha.html',
        form_class=ResetPasswordForm,
        success_url=reverse_lazy('verifique_email'),
    ), name='esqueci_senha'),

    path('senha/resetar/enviado/', PasswordResetDoneView.as_view(
        template_name='usuarios/acesso/verifique_email.html'
    ), name='verifique_email'),

    path('senha/resetar/confirmar/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='usuarios/acesso/redefinir_senha.html',
        form_class=MinhaSetPasswordForm,
        success_url=reverse_lazy('senha_redefinida'),
    ), name='password_reset_confirm'),

    path('senha/resetar/completo/', PasswordResetCompleteView.as_view(
        template_name='usuarios/acesso/senha_redefinida.html'
    ), name='senha_redefinida'),

]
