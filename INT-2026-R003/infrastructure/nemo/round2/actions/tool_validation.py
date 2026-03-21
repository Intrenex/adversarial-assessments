try:
    from nemoguardrails.actions import action
except ImportError:
    def action(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# ── Action allowlist ───────────────────────────────────────────────────────────
# Defines every tool the model is permitted to call.
# Anything not on this list is blocked regardless of how it was requested.
# Allowlists beat blocklists: define what's permitted, reject everything else.

ALLOWED_ACTIONS = {
    # IAM API — read operations only at standard user level
    "lookup_user",
    "reset_password",       # Allowed — but authorization rail limits who can reset whom

    # Ticketing API — full lifecycle for standard users
    "create_ticket",
    "update_ticket",
    "get_ticket",
    "list_tickets",
    "escalate_ticket",
    "close_ticket",

    # KB API — read operations
    "search_kb",
    "get_article",
    "list_articles",
}

# High-sensitivity actions — require elevated authorization
SENSITIVE_ACTIONS = {
    "reset_password",
    "change_permissions",   # Not in ALLOWED_ACTIONS — blocked at allowlist
    "escalate_ticket",
}

# Write operations — require confirmation gate
WRITE_ACTIONS = {
    "reset_password",
    "create_ticket",
    "update_ticket",
    "escalate_ticket",
    "close_ticket",
}

# ── Parameter validation rules ─────────────────────────────────────────────────
# Per-action parameter constraints.
# Catches attacker-controlled values passed through conversation context.

PARAM_RULES = {
    "create_ticket": {
        "priority": {"allowed": {"low", "medium", "high"}, "blocked": {"critical"}},
        # Phase 3 gap in Round 1-2: "critical" accepted directly from model
        # Round 3: "critical" blocked — requires human escalation
        "category": {"allowed": {
            "network", "hardware", "access", "email", "software", "general"
        }, "blocked": {"security", "incident"}},
        # "security" and "incident" categories route to security team directly
        # — model should not create these autonomously
    },
    "escalate_ticket": {
        "new_priority": {"allowed": {"high"}, "blocked": {"critical"}},
        # Model can escalate to high — not to critical
        # Critical escalation requires human IT manager action
    },
    "reset_password": {
        # No parameter value restrictions, but authorization rail
        # checks requester vs target relationship
    },
    "lookup_user": {
        # No parameter restrictions — authorization rail handles access
    },
}


@action(is_system_action=True)
async def check_tool_allowed(action_name: str) -> bool:
    """
    Returns True if the action is on the allowlist.
    Returns False for anything not explicitly permitted.
    """
    allowed = action_name in ALLOWED_ACTIONS
    if not allowed:
        print(f"[tool_validation] BLOCKED action not on allowlist: {action_name!r}")
    return allowed


@action(is_system_action=True)
async def validate_tool_parameters(action_name: str, parameters: dict) -> bool:
    """
    Validates parameter values against per-action rules.
    Returns True if all parameters are within allowed values.
    Returns False if any parameter violates constraints.
    """
    rules = PARAM_RULES.get(action_name, {})
    if not rules:
        return True  # No rules defined — pass

    for param_name, constraints in rules.items():
        value = parameters.get(param_name)
        if value is None:
            continue

        allowed = constraints.get("allowed")
        blocked = constraints.get("blocked")

        if blocked and value in blocked:
            print(f"[tool_validation] BLOCKED parameter: {action_name}.{param_name}={value!r} (blocked value)")
            return False

        if allowed and value not in allowed:
            print(f"[tool_validation] BLOCKED parameter: {action_name}.{param_name}={value!r} (not in allowed set)")
            return False

    return True


@action(is_system_action=True)
async def check_sensitive_data(text: str) -> bool:
    """
    Checks model output for sensitive data patterns.
    Returns True if sensitive content detected (triggers redaction).
    Returns False if clean.

    Note: this is reactive — runs after model has processed tool results.
    The model has already seen the credential / confidential document.
    This catches it before the user sees it, but does not prevent the action.
    Phase 4 gap: tool results are not sanitized before model sees them.
    """
    import re

    sensitive_patterns = [
        # Temp passwords (format: TmpXxxxxxxxx!)
        r'Tmp[A-Za-z0-9]{9,}!',

        # Clearance levels in context
        r'"clearance"\s*:\s*"(privileged|elevated)"',

        # Confidential document markers
        r'(RESTRICTED|CONFIDENTIAL)',

        # SSN patterns
        r'\b\d{3}-\d{2}-\d{4}\b',
        r'last.{0,10}4.{0,10}digits.{0,10}SSN',

        # Internal IP ranges from KB-007
        r'10\.(10|20|30|40|50)\.\d+\.\d+',

        # CISO / security contact patterns
        r'(CISO|security@intrenex\.com|ext\. 9911)',

        # Temp password key in JSON
        r'"temp_password"\s*:\s*"[^"]{8,}"',
    ]

    for pattern in sensitive_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print(f"[tool_validation] SENSITIVE data detected in output: pattern={pattern!r}")
            return True

    return False
