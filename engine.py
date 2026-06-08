"""
Diagnosis Engine — pure Python, no side effects.

Computes a weighted match score for each Disease against a submitted
set of symptom IDs and returns results sorted by score descending.
"""

from .models import Disease


def run_diagnosis(symptom_ids: list[int]) -> list[dict]:
    """
    For each Disease, compute:
        matched_weight = sum of weights for symptoms in symptom_ids
        total_weight   = sum of all weights for all symptoms of that disease
        match_score    = round(matched_weight / total_weight * 100, 1)

    Returns a list of result dicts sorted by match_score descending,
    only including diseases with match_score > 0.
    Each dict: {'disease': <Disease instance>, 'match_score': <float>}
    """
    submitted = set(symptom_ids)
    results = []

    for disease in Disease.objects.prefetch_related('diseasesymptom_set'):
        symptom_weights = {
            ds.symptom_id: ds.weight
            for ds in disease.diseasesymptom_set.all()
        }
        total_weight = sum(symptom_weights.values())
        if total_weight == 0:
            continue

        matched_weight = sum(
            w for sid, w in symptom_weights.items() if sid in submitted
        )
        if matched_weight == 0:
            continue

        match_score = round(matched_weight / total_weight * 100, 1)
        results.append({
            'disease': disease,
            'match_score': match_score,
        })

    return sorted(results, key=lambda r: r['match_score'], reverse=True)
