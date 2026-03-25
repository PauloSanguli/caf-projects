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
