from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import ProfessorAuthenticationForm

urlpatterns = [
    path("", views.submeter_projecto, name="submeter_projecto"),
    path(
        "consultar/",
        views.consultar_projectos_estudantes,
        name="consultar_projectos_estudantes",
    ),
    path(
        "professor/entrar/",
        auth_views.LoginView.as_view(
            template_name="submissions/professor_login.html",
            authentication_form=ProfessorAuthenticationForm,
            redirect_authenticated_user=False,
        ),
        name="professor_login",
    ),
    path(
        "professor/sair/",
        auth_views.LogoutView.as_view(next_page="/"),
        name="professor_logout",
    ),
    path(
        "professor/remover/<int:pk>/",
        views.remover_submissao_professor,
        name="remover_submissao_professor",
    ),
    path(
        "professor/download/<int:pk>/<str:kind>/",
        views.download_ficheiro_professor,
        name="professor_download_ficheiro",
    ),
    path("professor/", views.listar_projectos, name="lista_projectos_professor"),
]
