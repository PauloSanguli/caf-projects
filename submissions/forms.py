from django import forms
from django.core.validators import FileExtensionValidator

from .models import Classe, ProjectSubmission, Turma

MAX_ZIP_BYTES = 50 * 1024 * 1024
MAX_PDF_BYTES = 10 * 1024 * 1024


class ProjectSubmissionForm(forms.ModelForm):
    class Meta:
        model = ProjectSubmission
        fields = [
            "nome_projecto",
            "nome_responsavel",
            "membros_grupo",
            "classe",
            "turma",
            "sala",
            "ficheiro_projecto",
            "ficheiro_ata",
        ]
        widgets = {
            "nome_projecto": forms.TextInput(
                attrs={
                    "placeholder": "Ex: Sistema de Gestão Escolar",
                    "autocomplete": "off",
                    "class": "input-lg",
                }
            ),
            "nome_responsavel": forms.TextInput(
                attrs={
                    "placeholder": "Nome completo do representante",
                    "autocomplete": "name",
                }
            ),
            "membros_grupo": forms.TextInput(
                attrs={
                    "placeholder": "Ex: João Silva, Maria Santos",
                    "autocomplete": "off",
                }
            ),
            "sala": forms.TextInput(attrs={"placeholder": "Ex: 12", "autocomplete": "off"}),
            "classe": forms.Select(
                attrs={
                    "class": "field-select",
                    "aria-label": "Classe",
                }
            ),
            "turma": forms.Select(
                attrs={
                    "class": "field-select",
                    "aria-label": "Turma",
                }
            ),
            "ficheiro_projecto": forms.FileInput(
                attrs={
                    "accept": ".zip,application/zip",
                    "class": "dropzone-input",
                }
            ),
            "ficheiro_ata": forms.FileInput(
                attrs={"accept": ".pdf,application/pdf", "class": "dropzone-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nome_projecto"].label = "Nome do Projecto (Opcional)"
        self.fields["nome_responsavel"].label = "Aluno Responsável"
        self.fields["membros_grupo"].label = (
            "Outros Membros do Grupo (Separados por vírgula)"
        )
        self.fields["classe"].label = "Classe"
        self.fields["turma"].label = "Turma"
        self.fields["ficheiro_projecto"].label = "Código fonte (ZIP)"
        self.fields["ficheiro_ata"].label = "Actas e documentação (PDF)"

        self.fields["classe"].choices = [("", "Seleccionar")] + list(Classe.choices)
        self.fields["turma"].choices = [("", "Seleccionar")] + list(Turma.choices)

        self.fields["ficheiro_projecto"].validators.append(
            FileExtensionValidator(
                ["zip"],
                message="Apenas ficheiros com extensão .zip são aceites.",
            )
        )
        self.fields["ficheiro_ata"].validators.append(
            FileExtensionValidator(
                ["pdf"],
                message="Apenas ficheiros com extensão .pdf são aceites.",
            )
        )
        self.fields["nome_responsavel"].required = True
        self.fields["membros_grupo"].required = True
        self.fields["sala"].required = True

    def clean_ficheiro_projecto(self):
        f = self.cleaned_data.get("ficheiro_projecto")
        if not f:
            raise forms.ValidationError("É obrigatório enviar o projecto em formato ZIP.")
        name = getattr(f, "name", "") or ""
        if not name.lower().endswith(".zip"):
            raise forms.ValidationError("Apenas ficheiros .zip são aceites para o projecto.")
        if f.size > MAX_ZIP_BYTES:
            raise forms.ValidationError(
                "O ficheiro ZIP não pode exceder 50 MB."
            )
        return f

    def clean_ficheiro_ata(self):
        f = self.cleaned_data.get("ficheiro_ata")
        if not f:
            raise forms.ValidationError("É obrigatório enviar a ata em PDF.")
        name = getattr(f, "name", "") or ""
        if not name.lower().endswith(".pdf"):
            raise forms.ValidationError("Apenas ficheiros .pdf são aceites para a ata.")
        if f.size > MAX_PDF_BYTES:
            raise forms.ValidationError(
                "O ficheiro PDF não pode exceder 10 MB."
            )
        return f
