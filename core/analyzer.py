from core.llm_client import call_chat, parse_json_response

def extract_claim(post_text):
    messages = [
        {"role": "system", "content": "You are a fact-checking assistant."},
        {"role": "user", "content": f"Extract the SINGLE main factual claim from this text as one short sentence. If there is no clear factual claim, return exactly 'NO_CLAIM'.\n\nText: {post_text}"}
    ]
    return call_chat(messages)

def search_evidence(claim):
    # In a full production version, this would call SerpAPI/Google
    # For now, we return a generic placeholder or could implement real SerpAPI if key exists
    return []

def analyze_claim(claim, evidence, brand_name):
    evidence_text = "No direct evidence found via API. Rely on internal knowledge."
    if evidence:
        evidence_text = "\n".join([f"- {e['title']}: {e['snippet']}" for e in evidence])
    
    prompt = f"""
    You are an expert PR Crisis Manager.
    
    CLAIM: "{claim}"
    BRAND: "{brand_name}"
    EVIDENCE: {evidence_text}
    
    TASK:
    1. Determine verdict: "True", "Misleading", "False", or "Unclear".
    2. Assign confidence (0-100).
    3. Write explanation (2 sentences).
    4. Write a PR-safe response for the brand.
    
    OUTPUT JSON ONLY:
    {{
        "verdict": "string",
        "confidence": int,
        "explanation": "string",
        "sources": [],
        "pr_response": "string"
    }}
    """
    
    messages = [{"role": "system", "content": "You are a JSON machine."},
                {"role": "user", "content": prompt}]
    
    raw = call_chat(messages)
    return parse_json_response(raw)