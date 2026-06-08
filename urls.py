"""
Diagnosis URL patterns.

All routes are included under /api/v1/ via config/api_router.py.
"""

from django.urls import path

from .views import DiagnosisHistoryView, DiagnosisView, SymptomListView

urlpatterns = [
    path("symptoms/", SymptomListView.as_view()),
    path("diagnosis/", DiagnosisView.as_view()),
    path("diagnosis/history/", DiagnosisHistoryView.as_view()),
]
