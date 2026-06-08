"""
Diagnosis views.

- SymptomListView:      GET  /api/v1/symptoms/
- DiagnosisView:        POST /api/v1/diagnosis/
- DiagnosisHistoryView: GET  /api/v1/diagnosis/history/
"""

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsFarmer

from .engine import run_diagnosis
from .models import DiagnosisSession, Symptom
from .serializers import (
    DiagnosisHistorySerializer,
    DiagnosisInputSerializer,
    DiagnosisResultSerializer,
    SymptomSerializer,
)


class SymptomListView(APIView):
    """
    GET /api/v1/symptoms/
    Returns the full list of symptoms available for selection.
    Requires: Farmer role.
    """

    permission_classes = [IsFarmer]

    def get(self, request):
        symptoms = Symptom.objects.all()
        serializer = SymptomSerializer(symptoms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DiagnosisView(APIView):
    """
    POST /api/v1/diagnosis/
    Accepts a list of symptom_ids, runs the diagnosis engine, persists a
    DiagnosisSession, and returns ranked results.

    Request body:
        { "symptom_ids": [1, 3, 7] }

    Response body:
        {
            "session_id": 42,
            "results": [
                {
                    "disease_id": 5,
                    "name": "Newcastle Disease",
                    "match_score": 83.3,
                    "severity": "Severe",
                    "treatment_recommendations": "..."
                }
            ]
        }

    Requires: Farmer role.
    """

    permission_classes = [IsFarmer]

    def post(self, request):
        serializer = DiagnosisInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        symptom_ids = serializer.validated_data["symptom_ids"]

        # Run pure diagnosis engine (sorted by match_score desc, score > 0 only)
        results = run_diagnosis(symptom_ids)

        # Top result info (None when no diseases matched)
        top_disease = results[0]["disease"] if results else None
        top_score = results[0]["match_score"] if results else None

        # Persist the session
        session = DiagnosisSession.objects.create(
            farmer=request.user,
            top_disease=top_disease,
            top_score=top_score,
        )
        # Attach the submitted symptom IDs (silently ignores non-existent ones)
        session.symptoms.set(symptom_ids)

        result_serializer = DiagnosisResultSerializer(results, many=True)
        return Response(
            {
                "session_id": session.id,
                "results": result_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class DiagnosisHistoryView(ListAPIView):
    """
    GET /api/v1/diagnosis/history/

    Returns the authenticated Farmer's past DiagnosisSession records,
    ordered by most-recent first (-submitted_at).

    Requires: Farmer role.

    Response items:
        {
            "id": <int>,
            "submitted_at": <datetime>,
            "top_disease": {"id": <int>, "name": <str>} | null,
            "top_score": <float> | null,
            "symptoms": [{"id": <int>, "name": <str>}, ...]
        }
    """

    serializer_class = DiagnosisHistorySerializer
    permission_classes = [IsFarmer]

    def get_queryset(self):
        return (
            DiagnosisSession.objects
            .filter(farmer=self.request.user)
            .select_related('top_disease')
            .prefetch_related('symptoms')
            .order_by('-submitted_at')
        )
