"""
Admin registration for the diagnosis app.
"""

from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import DiagnosisSession, Disease, DiseaseSymptom, Symptom


class DiseaseSymptomInline(admin.TabularInline):
    model = DiseaseSymptom
    extra = 1
    min_num = 1


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    inlines = [DiseaseSymptomInline]
    list_display = ('name', 'severity')
    list_filter = ('severity',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if not obj.diseasesymptom_set.filter(weight__gt=0).exists():
            raise ValidationError(
                'A disease must have at least one symptom with a weight greater than 0.'
            )

    def clean(self):
        """Validate that at least one DiseaseSymptom with weight > 0 exists."""
        # Inline validation is handled in save_related; this hook is for
        # form-level clean in custom forms if wired up.
        pass


@admin.register(DiseaseSymptom)
class DiseaseSymptomAdmin(admin.ModelAdmin):
    list_display = ('disease', 'symptom', 'weight')


@admin.register(DiagnosisSession)
class DiagnosisSessionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'farmer', 'submitted_at', 'top_disease', 'top_score')
    list_filter = ('farmer',)
    readonly_fields = (
        'farmer',
        'submitted_at',
        'symptoms',
        'top_disease',
        'top_score',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
