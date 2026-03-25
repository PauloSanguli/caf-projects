from django.urls import path

from . import views

urlpatterns = [
    path("", views.submeter_projecto, name="submeter_projecto"),
    path("professor/", views.listar_projectos, name="lista_projectos_professor"),
]
