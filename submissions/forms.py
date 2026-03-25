from django import forms
from django.core.validators import FileExtensionValidator

from .models import Classe, ProjectSubmission, Turma


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
                    "placeholder": "Ex.: Site da biblioteca escolar",
                    "autocomplete": "off",
                }
            ),
            "nome_responsavel": forms.TextInput(
                attrs={
                    "placeholder": "Nome completo",
                    "autocomplete": "name",
                }
            ),
            "membros_grupo": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Ana Silva, Bruno Costa, … ou um nome por linha",
                }
            ),
            "sala": forms.TextInput(attrs={"placeholder": "Ex.: 12", "autocomplete": "off"}),
            "classe": forms.Select(
                attrs={
                    "class": "field-select",
                    "aria-label": "Classe (10ª ou 11ª)",
                }
            ),
            "turma": forms.Select(
                attrs={
                    "class": "field-select",
                    "aria-label": "Turma",
                }
            ),
            "ficheiro_projecto": forms.ClearableFileInput(
                attrs={"accept": ".zip,application/zip"}
            ),
            "ficheiro_ata": forms.ClearableFileInput(attrs={"accept": ".pdf,application/pdf"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["classe"].label = "Classe"
        self.fields["turma"].label = "Turma"
        self.fields["classe"].choices = [
            ("", "— Seleccione a classe —"),
        ] + list(Classe.choices)
        self.fields["turma"].choices = [
            ("", "— Seleccione a turma —"),
        ] + list(Turma.choices)

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
        return f

    def clean_ficheiro_ata(self):
        f = self.cleaned_data.get("ficheiro_ata")
        if not f:
            raise forms.ValidationError("É obrigatório enviar a ata em PDF.")
        name = getattr(f, "name", "") or ""
        if not name.lower().endswith(".pdf"):
            raise forms.ValidationError("Apenas ficheiros .pdf são aceites para a ata.")
        return f
