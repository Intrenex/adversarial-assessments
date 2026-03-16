# elastic_logger.py

import os
import requests
import urllib3
from datetime import datetime, timezone
from pyrit.memory import CentralMemory

urllib3.disable_warnings()

ES_URL_CANDIDATES = [
    os.getenv("IX_ELASTIC_URL"),
    "https://ecp-elasticsearch:9200",
    "https://172.17.0.1:9200",
]
ES_AUTH = ("elastic", "elastic")
ES_INDEX = "ix-adversarial-sessions"


def _resolve_es_url():
    for url in ES_URL_CANDIDATES:
        if not url:
            continue
        try:
            response = requests.get(url, auth=ES_AUTH, verify=False, timeout=3)
            if response.ok:
                return url
        except Exception:
            continue
    return ES_URL_CANDIDATES[1]


ES_URL = _resolve_es_url()


def log_turn_to_elastic(session_id, turn, role, strategy, content,
                        phase=None, objective=None, achieved=False,
                        turn_total=None, model_target=None,
                        model_attacker=None, finding_tags=None):
    doc = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "phase": phase,
        "objective": objective,
        "achieved_objective": achieved,
        "turn_number": turn,
        "turn_total": turn_total,
        "role": role,
        "strategy": strategy,
        "content": content,
        "word_count": len(content.split()),
        "model_target": model_target,
        "model_attacker": model_attacker,
        "finding_tags": finding_tags or []
    }
    try:
        response = requests.post(
            f"{ES_URL}/{ES_INDEX}/_doc",
            json=doc,
            auth=ES_AUTH,
            verify=False
        )
        if response.status_code != 201:
            print(f"❌ Elastic error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"⚠️ Network failure: {e}")


def log_results_to_elastic(results, session_id, strategy,
                           phase=None, objective=None,
                           model_target=None, model_attacker=None):
    memory = CentralMemory.get_memory_instance()

    for result in results:
        conv_id = getattr(result, 'conversation_id', None)
        if not conv_id:
            print("⚠️ Result has no conversation_id to query.")
            continue

        conversation_pieces = memory.get_conversation(conversation_id=conv_id)
        if not conversation_pieces:
            print(f"⚠️ No data found in memory for ID: {conv_id}")
            continue

        filtered_pieces = [p for p in conversation_pieces if getattr(p, 'role', None) in ['user', 'assistant']]
        turn_total = len(filtered_pieces)
        achieved = getattr(result, 'achieved_objective', False)

        print(f"📤 Found {turn_total} valid turns. Sending to Elastic...")

        for i, piece in enumerate(filtered_pieces):
            role = getattr(piece, 'role', 'unknown')
            content = (
                getattr(piece, 'converted_value', None) or
                getattr(piece, 'original_value', None) or
                getattr(piece, 'text', None) or
                str(piece)
            )

            log_turn_to_elastic(
                session_id=session_id,
                turn=i + 1,
                role=role,
                strategy=strategy,
                content=content,
                phase=phase,
                objective=objective,
                achieved=achieved,
                turn_total=turn_total,
                model_target=model_target,
                model_attacker=model_attacker,
                finding_tags=["objective_achieved"] if achieved else []
            )
