import csv
import io
import zipfile
from datetime import datetime, time
from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from botocore.exceptions import ClientError

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


def _deadline_entrega_hoje_14h_ms():
    """
    Hoje às 14:00 no fuso activo (TIME_ZONE).
    Devolve milissegundos Unix para o JS — evita erros de 1h no parse de ISO no browser.
    """
    tz = timezone.get_current_timezone()
    local_date = timezone.localtime().date()
    naive = datetime.combine(local_date, time(14, 0))
    deadline = timezone.make_aware(naive, tz)
    return int(deadline.timestamp() * 1000)


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
    return render(
        request,
        "submissions/submeter.html",
        {
            "form": form,
            "deadline_entrega_ms": _deadline_entrega_hoje_14h_ms(),
        },
    )


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
def download_ficheiro_professor(request, pk, kind):
    """
    Descarrega ZIP/PDF via Django (streaming com credenciais do servidor).
    Evita depender de URLs pré-assinadas S3/Supabase no browser (Missing signature, etc.).
    """
    submission = get_object_or_404(ProjectSubmission, pk=pk)
    if kind == "zip":
        field = submission.ficheiro_projecto
        download_name = "projecto.zip"
        content_type = "application/zip"
    elif kind == "pdf":
        field = submission.ficheiro_ata
        download_name = "ata.pdf"
        content_type = "application/pdf"
    else:
        raise Http404()
    if not field or not field.name:
        raise Http404()
    try:
        fh = field.open("rb")
    except OSError:
        raise Http404()
    except ClientError:
        raise Http404()
    return FileResponse(
        fh,
        as_attachment=True,
        filename=download_name,
        content_type=content_type,
    )


def _csv_grupo_bytes(submission):
    """UTF-8 com BOM para Excel; colunas nome, turma, sala, nota."""
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["nome", "turma", "sala", "nota"])
    nota_str = ""
    if submission.nota is not None:
        nota_str = str(submission.nota).replace(".", ",")
    turma = submission.turma
    sala = submission.sala
    for nome in submission.nomes_alunos_grupo():
        w.writerow([nome, turma, sala, nota_str])
    return out.getvalue().encode("utf-8-sig")


@user_passes_test(_is_professor)
def professor_baixar_tudo(request):
    """
    ZIP com todas as submissões visíveis (filtros classe/turma),
    mesma árvore que no storage + grupo.csv por pasta.
    """
    qs = ProjectSubmission.objects.all().order_by("-data_submissao")
    classe = request.GET.get("classe") or ""
    turma = request.GET.get("turma") or ""
    if classe in {Classe.DEZ, Classe.ONZE}:
        qs = qs.filter(classe=classe)
    if turma in {Turma.IF, Turma.ID, Turma.IB, Turma.IG}:
        qs = qs.filter(turma=turma)

    if not qs.exists():
        return HttpResponse(
            "Não há submissões para descarregar com os filtros actuais.",
            status=404,
            content_type="text/plain; charset=utf-8",
        )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for sub in qs:
            base = sub.caminho_pasta_grupo().replace("\\", "/")
            zf.writestr(f"{base}/grupo.csv", _csv_grupo_bytes(sub))
            pairs = (
                (sub.ficheiro_projecto, "projecto.zip"),
                (sub.ficheiro_ata, "ata.pdf"),
            )
            for field, arcname in pairs:
                if not field or not field.name:
                    continue
                try:
                    with field.open("rb") as fh:
                        zf.writestr(f"{base}/{arcname}", fh.read())
                except (OSError, ClientError):
                    continue

    buf.seek(0)
    stamp = timezone.localtime().strftime("%Y%m%d-%H%M")
    filename = f"caf-projectos-{stamp}.zip"
    return FileResponse(
        buf,
        as_attachment=True,
        filename=filename,
        content_type="application/zip",
    )


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
