"""Chatbot providers (implemented in Phase 9).

The service layer selects a provider from ``AI_PROVIDER``:

- ``demo``     — scripted, safe in-app responses (default development mode)
- ``external`` — calls an external LLM using ``AI_API_KEY`` (never exposed
  to the frontend)

Safety contract: the assistant never diagnoses, never prescribes, never
makes emergency decisions, and never claims certainty about a condition.
"""


def chat_response(user_message, provider="demo"):
    """Return an assistant reply for ``user_message``.

    Placeholder -- implemented in Phase 9.
    """
    raise NotImplementedError("chat_response() is implemented in Phase 9")