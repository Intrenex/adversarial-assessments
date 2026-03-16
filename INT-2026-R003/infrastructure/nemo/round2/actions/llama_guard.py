import httpx
from nemoguardrails.actions import action

LLAMA_GUARD_URL = "http://llama_guard:11434/api/chat"
LLAMA_GUARD_MODEL = "llama-guard3:8b"

@action(is_system_action=True)
async def llama_guard_check(text: str, role: str = "user") -> bool:
    if role == "user":
        messages = [{"role": "user", "content": text}]
    else:
        messages = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": text}
        ]
    payload = {
        "model": LLAMA_GUARD_MODEL,
        "messages": messages,
        "stream": False
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(LLAMA_GUARD_URL, json=payload)
            if response.status_code != 200:
                print(f"Llama Guard Error: Status {response.status_code}")
                return False
            result = response.json()
            content = result.get("message", {}).get("content", "").strip().lower()
            return "unsafe" not in content
    except Exception as e:
        print(f"Llama Guard Connection Error: {e}")
        return False
