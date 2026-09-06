"""Recommendation engine helpers (implemented in Phase 8).

Interfaces are defined here so ``backend/app/services/recommendation_service.py``
can depend on them without change later.

Safety contract:
- Returns a *suggested department*, never a diagnosis.
- Low confidence -> "consult a qualified practitioner", no forced mapping.
"""


def recommend(concern_text, provider="rule"):
    """Return a department suggestion for ``concern_text``.

    Placeholder -- implemented in Phase 8.
    """
    raise NotImplementedError("recommend() is implemented in Phase 8")