import httpx
from nemoguardrails.actions import action

CLASSIFIER_URL   = "http://ollama:11434/api/chat"
CLASSIFIER_MODEL = "ix-scope-classifier:latest"

# Prompt is now minimal — stable scope context is baked into the
# ix-scope-classifier Modelfile system prompt.
# This template only passes the user message for classification.
PROMPT_TEMPLATE = """Classify this user message:

{user_input}"""


@action(is_system_action=True)
async def check_topic_scope(text: str) -> bool:
    """
    Returns True if the message is requesting a permitted IT support action.
    Returns False if out of scope — triggers bot refuse off topic.
    """
    prompt = PROMPT_TEMPLATE.format(user_input=text)
    payload = {
        "model":   CLASSIFIER_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream":  False,
        "options": {"temperature": 0.0},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(CLASSIFIER_URL, json=payload)
            response.raise_for_status()
            result  = response.json()
            verdict = result.get("message", {}).get("content", "").strip().upper()

            if "OUT_OF_SCOPE" in verdict:
                return False
            if "IN_SCOPE" in verdict:
                return True

            # Fail closed — ambiguous response treated as out of scope
            print(f"[topic_scope] Ambiguous response: {verdict!r} — failing closed")
            return False

    except Exception as e:
        print(f"[topic_scope] Error: {e}")
        return False  # Fail closed
