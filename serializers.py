"""
Serializers for the Diagnosis app.
"""

from rest_framework import serializers

from .models import DiagnosisSession, Disease, Symptom


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ('id', 'name')


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ('id', 'name')


class DiagnosisHistorySerializer(serializers.ModelSerializer):
    """
    Serializes a DiagnosisSession for the history list endpoint.

    Fields returned:
        id, submitted_at,
        top_disease: {id, name},
        top_score,
        symptoms: [{id, name}]
    """

    top_disease = DiseaseSerializer(read_only=True)
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = DiagnosisSession
        fields = ('id', 'submitted_at', 'top_disease', 'top_score', 'symptoms')


class DiagnosisInputSerializer(serializers.Serializer):
    """Validates the symptom_ids submitted to POST /diagnosis/."""

    symptom_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        error_messages={
            "min_length": "symptom_ids must not be empty.",
            "required": "symptom_ids is required.",
        },
    )


class DiagnosisResultSerializer(serializers.Serializer):
    """
    Serializes a single result dict produced by run_diagnosis().

    Expected dict shape:
        {'disease': <Disease instance>, 'match_score': <float>}
    """

    disease_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    match_score = serializers.FloatField()
    severity = serializers.SerializerMethodField()
    treatment_recommendations = serializers.SerializerMethodField()

    def get_disease_id(self, obj):
        return obj["disease"].id

    def get_name(self, obj):
        return obj["disease"].name

    def get_severity(self, obj):
        return obj["disease"].severity

    def get_treatment_recommendations(self, obj):
        return obj["disease"].treatment_recommendations
