from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ProjectSubmissionForm
from .models import Classe, ProjectSubmission, Turma


def submeter_projecto(request):
    if request.method == "POST":
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Submissão recebida com sucesso. Obrigado.",
            )
            return redirect("submeter_projecto")
        messages.error(
            request,
            "Corrija os erros indicados abaixo e tente novamente.",
        )
    else:
        form = ProjectSubmissionForm()
    return render(request, "submissions/submeter.html", {"form": form})


def listar_projectos(request):
    qs = ProjectSubmission.objects.all()
    classe = request.GET.get("classe") or ""
    turma = request.GET.get("turma") or ""

    if classe in {Classe.DEZ, Classe.ONZE}:
        qs = qs.filter(classe=classe)
    if turma in {Turma.IF, Turma.ID, Turma.IB, Turma.IG}:
        qs = qs.filter(turma=turma)

    context = {
        "projectos": qs,
        "filtro_classe": classe,
        "filtro_turma": turma,
        "classes": Classe.choices,
        "turmas": Turma.choices,
        "total": qs.count(),
    }
    return render(request, "submissions/lista_professor.html", context)


def consultar_projectos_estudantes(request):
    """Lista pública de submissões por classe/turma em cards (carrossel)."""
    classe = request.GET.get("classe") or ""
    turma = request.GET.get("turma") or ""
    projectos = []
    titulo_secao = ""
    mostrar_resultados = False

    if classe in {Classe.DEZ, Classe.ONZE} and turma in {
        Turma.IF,
        Turma.ID,
        Turma.IB,
        Turma.IG,
    }:
        mostrar_resultados = True
        projectos = list(
            ProjectSubmission.objects.filter(classe=classe, turma=turma).order_by(
                "-data_submissao"
            )
        )
        classe_label = dict(Classe.choices)[classe]
        titulo_secao = f"{classe_label} · Turma {turma}"

    context = {
        "projectos": projectos,
        "filtro_classe": classe,
        "filtro_turma": turma,
        "classes": Classe.choices,
        "turmas": Turma.choices,
        "mostrar_resultados": mostrar_resultados,
        "titulo_secao": titulo_secao,
        "total": len(projectos),
    }
    return render(request, "submissions/consultar_estudantes.html", context)
