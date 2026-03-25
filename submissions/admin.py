from django.contrib import admin

from .models import ProjectSubmission


@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "titulo_curto",
        "nome_responsavel",
        "classe",
        "turma",
        "sala",
        "data_submissao",
        "nota",
    )

    @admin.display(description="Nome do projecto")
    def titulo_curto(self, obj):
        t = (obj.nome_projecto or "").strip()
        return t or "—"
    list_filter = ("classe", "turma", "data_submissao")
    search_fields = ("nome_projecto", "nome_responsavel", "membros_grupo")
    readonly_fields = ("folder_id", "data_submissao")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "folder_id",
                    "nome_projecto",
                    "nome_responsavel",
                    "membros_grupo",
                    "classe",
                    "turma",
                    "sala",
                )
            },
        ),
        (
            "Ficheiros",
            {"fields": ("ficheiro_projecto", "ficheiro_ata")},
        ),
        (
            "Avaliação",
            {"fields": ("nota",)},
        ),
        (
            "Metadados",
            {"fields": ("data_submissao",)},
        ),
    )
