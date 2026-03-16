import time
from collections import defaultdict
from threading import Lock
try:
    from nemoguardrails.actions import action
except ImportError:
    def action(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# ── Rate limiting ──────────────────────────────────────────────────────────────
# Time-window rate limiting — industry standard pattern.
# Tracks action counts in a rolling one-hour window keyed by stable source
# identifier so limits accumulate across multi-turn conversations.
#
# Key: (source_identifier, action_name) → list[timestamp]
_time_windows: dict = defaultdict(list)
_lock = Lock()

# Per-action limits per hour
ACTION_LIMITS_PER_HOUR = {
    "reset_password": 5,       # Max 5 resets per hour per source
    "change_permissions": 1,   # Should never reach here (allowlist blocks it)
    "escalate_ticket": 10,     # Max 10 escalations per hour
    "lookup_user": 50,         # Max 50 lookups per hour
    "create_ticket": 20,       # Max 20 ticket creates per hour
    "search_kb": 100,          # Max 100 KB searches per hour
    "get_article": 50,         # Max 50 article fetches per hour
}
WINDOW_SECONDS = 3600
CURRENT_SOURCE = "default"


@action(is_system_action=True)
async def check_rate_limit(action_name: str, session_id: str | None = None) -> bool:
    """
    Time-window rate limiting.
    Tracks action counts within a rolling hour window.
    Falls back gracefully — allows action if limit not configured.
    """
    limit = ACTION_LIMITS_PER_HOUR.get(action_name)
    if limit is None:
        return True

    source = session_id or CURRENT_SOURCE
    key = (source, action_name)
    now = time.time()
    window_start = now - WINDOW_SECONDS

    with _lock:
        _time_windows[key] = [t for t in _time_windows[key] if t > window_start]
        current_count = len(_time_windows[key])

        if current_count >= limit:
            print(
                f"[rate_limiting] EXCEEDED: source={source!r} action={action_name!r} "
                f"count={current_count} limit={limit} window={WINDOW_SECONDS}s"
            )
            return False

        _time_windows[key].append(now)
        remaining = limit - (current_count + 1)
        print(
            f"[rate_limiting] OK: source={source!r} action={action_name!r} "
            f"count={current_count + 1}/{limit} remaining={remaining} window={WINDOW_SECONDS}s"
        )
        return True


@action(is_system_action=True)
async def get_session_refusal_count() -> int:
    """
    Returns number of refused requests in current session.
    Used by dialog.co to detect repeated probing patterns.
    Placeholder — full implementation tracks refusals in session state.
    """
    return 0


@action(is_system_action=True)
async def log_probe_pattern(turn_count: int, user_message: str) -> bool:
    """
    Logs repeated probing pattern for Elastic pickup.
    Does not block — detection only.
    """
    print(f"[rate_limiting] PROBE PATTERN DETECTED: refusals={turn_count} msg={user_message[:100]!r}")
    return True
