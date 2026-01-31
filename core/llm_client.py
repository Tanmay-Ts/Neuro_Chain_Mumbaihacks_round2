"""
llm_client.py

Responsible for:
- Calling the LLM safely
- Drafting AI-assisted responses
- Recording time-to-response
- Writing ledger events

NO business logic.
NO risk logic.
NO UI logic.
"""

from openai import OpenAI
from datetime import datetime
from sqlalchemy.orm import Session

from config import (
    OPENAI_API_KEY,
    OPENAI_ORG_ID,
    OPENAI_PROJECT_ID,
)
from core.ledger import IncidentLedger


# =========================================================
# OpenAI Client Initialization (Responses API)
# =========================================================

def create_openai_client():
    """
    Create OpenAI client with proper auth context.
    Organization & project are optional but supported.
    """

    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API key not configured")

    client_kwargs = {
        "api_key": OPENAI_API_KEY,
    }

    if OPENAI_ORG_ID:
        client_kwargs["organization"] = OPENAI_ORG_ID

    if OPENAI_PROJECT_ID:
        client_kwargs["project"] = OPENAI_PROJECT_ID

    return OpenAI(**client_kwargs)


# Singleton client
_openai_client = create_openai_client()


# =========================================================
# LLM Client Wrapper
# =========================================================

class LLMClient:
    """
    Handles AI-assisted response drafting.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.ledger = IncidentLedger(db_session)

    # -----------------------------------------------------
    # Response drafting
    # -----------------------------------------------------

    def draft_response(
        self,
        incident,
        context: str,
    ) -> str:
        """
        Generate an AI-assisted response draft.

        Side effects:
        - Sets response_drafted_at
        - Updates incident status
        - Writes ledger event
        """

        prompt = self._build_prompt(incident, context)

        response = _openai_client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.2,
        )

        # Extract plain text safely
        response_text = response.output_text.strip()

        # -------------------------------------------------
        # Lifecycle updates (TIME TO RESPONSE)
        # -------------------------------------------------

        incident.mark_responded(response_text)

        self.db.add(incident)
        self.db.commit()

        self.ledger.record_response_drafted(incident.id)

        return response_text

    # -----------------------------------------------------
    # Prompt construction (explicit & safe)
    # -----------------------------------------------------

    def _build_prompt(self, incident, context: str) -> str:
        """
        Constructs a PR-safe, non-opinionated prompt.
        """

        return f"""
You are assisting a professional public relations team.

Your task:
- Draft a calm, factual, non-defensive response
- Do NOT speculate
- Do NOT assign blame
- Do NOT verify truth
- Do NOT exaggerate
- Keep it concise and professional

Incident details:
- Title: {incident.title}
- Source: {incident.source}
- Risk level: {incident.risk_level}

Context:
{context}

Draft a response that a PR team can review and approve.
"""
# =========================================================
# BACKWARD-COMPATIBILITY LAYER
# =========================================================
# Keeps core.analyzer working without refactor
# =========================================================

import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_ORG_ID, OPENAI_PROJECT_ID

# Reuse same OpenAI client (Responses API)
_legacy_client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORG_ID or None,
    project=OPENAI_PROJECT_ID or None,
)

def call_chat(prompt: str, temperature: float = 0.2) -> str:
    """
    Legacy wrapper for analyzer.py.
    Returns raw text output from the LLM.
    """

    response = _legacy_client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=temperature,
    )

    return response.output_text.strip()


def parse_json_response(text: str):
    """
    Legacy JSON parser used by analyzer.
    Attempts strict JSON first, then fallback.
    """

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass

    return {
        "error": "Invalid JSON response",
        "raw": text
    }
