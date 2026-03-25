from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ProjectSubmissionForm
from .models import Classe, ProjectSubmission, Turma


def favicon_svg(request):
    """Serve /favicon.ico como SVG (evita 404 sem depender do URL de static)."""
    path = (
        Path(settings.BASE_DIR)
        / "submissions"
        / "static"
        / "submissions"
        / "favicon.svg"
    )
    if not path.is_file():
        raise Http404()
    return FileResponse(path.open("rb"), content_type="image/svg+xml")


def _is_professor(user):
    """Apenas contas activas com permissão de equipa (staff)."""
    return user.is_active and user.is_staff


def submeter_projecto(request):
    if request.method == "POST":
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Submissão recebida com sucesso. O envio foi registado.",
            )
            return redirect("submeter_projecto")
        messages.error(
            request,
            "Não foi possível concluir a submissão. Corrija os campos assinalados e tente novamente.",
        )
    else:
        form = ProjectSubmissionForm()
    return render(request, "submissions/submeter.html", {"form": form})


@user_passes_test(_is_professor)
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


@user_passes_test(_is_professor)
def remover_submissao_professor(request, pk):
    submission = get_object_or_404(ProjectSubmission, pk=pk)
    if request.method != "POST":
        return redirect("lista_projectos_professor")

    if submission.ficheiro_projecto:
        submission.ficheiro_projecto.delete(save=False)
    if submission.ficheiro_ata:
        submission.ficheiro_ata.delete(save=False)
    submission.delete()
    messages.success(
        request,
        "Grupo e ficheiros associados foram removidos.",
    )

    params = {}
    if request.POST.get("classe") in {Classe.DEZ, Classe.ONZE}:
        params["classe"] = request.POST["classe"]
    if request.POST.get("turma") in {Turma.IF, Turma.ID, Turma.IB, Turma.IG}:
        params["turma"] = request.POST["turma"]
    url = reverse("lista_projectos_professor")
    if params:
        url = f"{url}?{urlencode(params)}"
    return redirect(url)


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
