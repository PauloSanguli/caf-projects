import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Classe(models.TextChoices):
    DEZ = "10", _("10ª classe")
    ONZE = "11", _("11ª classe")


class Turma(models.TextChoices):
    IF = "IF", "IF"
    ID = "ID", "ID"
    IB = "IB", "IB"
    IG = "IG", "IG"


# Salas numeradas de 1 a 14 (valor e rótulo iguais)
SALA_CHOICES = [(str(i), str(i)) for i in range(1, 15)]


def _folder_name(instance):
    """
    Nome da pasta do grupo no disco:
    - Com nome do projecto: slug do título + sufixo do id (unicidade);
    - Sem nome (ou slug vazio): igual ao comportamento anterior (responsável + sufixo).
    """
    nome_proj = (instance.nome_projecto or "").strip()
    if nome_proj:
        base = slugify(nome_proj)[:48]
        if base:
            return f"{base}_{str(instance.folder_id)[:8]}"
    base = slugify(instance.nome_responsavel)[:48] or "grupo"
    return f"{base}_{str(instance.folder_id)[:8]}"


def upload_project_zip(instance, filename):
    base = os.path.join(
        f"classe_{instance.classe}",
        instance.turma,
        _folder_name(instance),
    )
    return os.path.join(base, "projecto.zip")


def upload_ata_pdf(instance, filename):
    base = os.path.join(
        f"classe_{instance.classe}",
        instance.turma,
        _folder_name(instance),
    )
    return os.path.join(base, "ata.pdf")


class ProjectSubmission(models.Model):
    """
    Submissão de projecto de estudantes.
    `folder_id` garante caminho de ficheiros estável antes do primeiro save (upload_to).
    `nota` reservado para avaliação futura.
    """

    folder_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    nome_projecto = models.CharField(
        "Nome do projecto",
        max_length=200,
        blank=True,
        help_text="Opcional, mas recomendável.",
    )
    nome_responsavel = models.CharField("Nome do estudante responsável", max_length=200)
    membros_grupo = models.TextField(
        "Membros do grupo",
        help_text="Um por linha ou separados por vírgulas.",
    )
    classe = models.CharField(
        max_length=2,
        choices=Classe.choices,
    )
    turma = models.CharField(
        max_length=2,
        choices=Turma.choices,
    )
    sala = models.CharField("Sala", max_length=2, choices=SALA_CHOICES)

    ficheiro_projecto = models.FileField(
        "Projecto (.zip)",
        upload_to=upload_project_zip,
        help_text="Ficheiro ZIP com HTML, CSS e opcionalmente JS.",
    )
    ficheiro_ata = models.FileField(
        "Ata em PDF",
        upload_to=upload_ata_pdf,
        help_text="PDF com a ata e descrição do projecto.",
    )

    data_submissao = models.DateTimeField(auto_now_add=True)
    nota = models.DecimalField(
        "Nota",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Para uso futuro na avaliação.",
    )

    class Meta:
        ordering = ["-data_submissao"]
        verbose_name = "submissão de projecto"
        verbose_name_plural = "submissões de projectos"

    def __str__(self):
        titulo = self.nome_projecto.strip() or "(sem nome)"
        return f"{titulo} — {self.nome_responsavel} ({self.classe} {self.turma})"

    def membros_lista(self):
        """Lista de membros a partir do texto livre."""
        raw = self.membros_grupo.replace("\n", ",")
        partes = [p.strip() for p in raw.split(",") if p.strip()]
        return partes
