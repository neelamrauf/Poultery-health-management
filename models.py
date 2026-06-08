"""
Diagnosis app models: Symptom, Disease, DiseaseSymptom, DiagnosisSession.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Disease(models.Model):
    SEVERITY_CHOICES = [
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe'),
    ]

    name = models.CharField(max_length=150, unique=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    treatment_recommendations = models.TextField()
    symptoms = models.ManyToManyField(Symptom, through='DiseaseSymptom')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DiseaseSymptom(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    weight = models.FloatField(default=1.0, validators=[MinValueValidator(0.001)])  # must be > 0

    class Meta:
        unique_together = ('disease', 'symptom')
        constraints = [
            models.CheckConstraint(
                check=models.Q(weight__gt=0),
                name='diseasesymptom_weight_gt_0',
            ),
        ]

    def __str__(self):
        return f'{self.disease.name} — {self.symptom.name} (weight: {self.weight})'


class DiagnosisSession(models.Model):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diagnosis_sessions',
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    symptoms = models.ManyToManyField(Symptom, blank=True)
    top_disease = models.ForeignKey(
        Disease,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='top_sessions',
    )
    top_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'Session #{self.pk} by {self.farmer.username} at {self.submitted_at}'
