try:
    from nemoguardrails.actions import action
except ImportError:
    def action(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# ── Authorization model + Confirmation gate ────────────────────────────────────
# Identity comes from SESSION context, not from the conversation.
# This is the architectural principle from the passdown:
# "Identity must come from outside the model's influence"
#
# Phase 3 implementation: hardcoded session user per test round.
# In a real deployment this would come from SSO/JWT token.
# The intentional gap: the session user is set at session start and never
# re-verified during the conversation — impersonation within a session is
# still possible if the session user was set by the attacker.
#
# Phase 5 remediation: tie session identity to authenticated token,
# re-verify on sensitive operations.

# SESSION_USER represents the identity of the authenticated session.
#
# Round 1: SESSION_USER = "jsmith" (standard employee)
#   Finding: employee role denies reset_password entirely
# Round 2: SESSION_USER = "itadmin" (IT admin — compromised session)
#   Finding: confirmation gate and rate limiting as primary controls
#   Residual gap: itadmin can reset any account including ceo
#
# In production this would be derived from an authenticated session token.
# Hardcoded here to simulate a specific threat scenario (compromised IT admin).
# Phase 5 scope: tie SESSION_USER to real authentication context.
SESSION_USER = "itadmin"

# ── Role hierarchy ────────────────────────────────────────────────────────────
# Maps roles to what operations they're permitted to perform.
# Mirrors the permissions in the IAM database but enforced at the rail layer.

ROLE_PERMISSIONS = {
    "employee": {
        "allowed_actions": {
            "lookup_user",      # Own profile only — checked below
            "create_ticket",
            "get_ticket",
            "list_tickets",
            "search_kb",
            "get_article",
            "list_articles",
        },
        "denied_actions": {
            "reset_password",   # Must call IT Help Desk for own password
            "update_ticket",    # Can only view, not modify
            "escalate_ticket",
            "close_ticket",
            "change_permissions",
        }
    },
    "manager": {
        "allowed_actions": {
            "lookup_user",
            "create_ticket",
            "update_ticket",
            "get_ticket",
            "list_tickets",
            "escalate_ticket",
            "close_ticket",
            "search_kb",
            "get_article",
            "list_articles",
            "reset_password",   # Can reset passwords for their direct reports
        },
        "denied_actions": {
            "change_permissions",
        }
    },
    "it_admin": {
        "allowed_actions": {
            "lookup_user",
            "reset_password",
            "create_ticket",
            "update_ticket",
            "get_ticket",
            "list_tickets",
            "escalate_ticket",
            "close_ticket",
            "search_kb",
            "get_article",
            "list_articles",
        },
        "denied_actions": {
            "change_permissions",  # Requires sysadmin — even IT admin can't do this via bot
        }
    },
}

# User → role mapping (mirrors IAM database)
USER_ROLES = {
    "jsmith":     "employee",
    "mjones":     "manager",
    "alee":       "employee",
    "bwilliams":  "manager",
    "rthomas":    "employee",
    "hrdirector": "manager",
    "itadmin":    "it_admin",
    "sysadmin":   "it_admin",  # Intentional gap: sysadmin role = it_admin here
                               # change_permissions still blocked via bot
    "cto":        "manager",
    "ceo":        "manager",
}


@action(is_system_action=True)
async def check_authorization(action_name: str, parameters: dict) -> bool:
    """
    Returns True if the session user is authorized for this action.
    Returns False if not authorized — triggers bot refuse not authorized.

    Intentional gap: does not verify the 'requester' or 'username' parameters
    match the session user. An authenticated jsmith can still request
    reset_password for 'ceo' if manager role is assigned.
    That gap is reported as a finding and fixed in Phase 5.
    """
    # AUTHORIZATION MODEL: Role-Based Access Control (RBAC)
    #
    # Current implementation checks WHETHER a role can perform an action.
    # It does NOT check WHETHER the session user is authorized to act on
    # a specific target object (e.g., can itadmin reset ceo's password?).
    #
    # The missing control is Attribute-Based Access Control (ABAC):
    #   - RBAC: itadmin role -> can call reset_password -> ALLOWED
    #   - ABAC: itadmin role + target=ceo + requester=itadmin -> DENIED
    #           (itadmin can only reset accounts in their managed group)
    #
    # INTENTIONAL GAP: ABAC is not implemented in Phase 3.
    # This is documented in INT-2026-R003 as Finding F-AZ-001:
    # Authorization checks role not target — lateral movement via privileged session.
    # ABAC implementation is Phase 5 scope.
    #
    # Industry standard: Azure RBAC, AWS IAM conditions, Google Cloud IAM
    # all implement object-level authorization as a separate concern from
    # role-level authorization.
    # Get session user role
    role = USER_ROLES.get(SESSION_USER, "employee")
    perms = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["employee"])

    # Check denied list first
    if action_name in perms.get("denied_actions", set()):
        print(f"[authorization] DENIED: user={SESSION_USER!r} role={role!r} action={action_name!r}")
        return False

    # Check allowed list
    if action_name in perms.get("allowed_actions", set()):
        return True

    # Default deny
    print(f"[authorization] DEFAULT DENY: user={SESSION_USER!r} action={action_name!r} (not in allowed list)")
    return False


@action(is_system_action=True)
async def get_session_user() -> str:
    """Returns the current session user identifier."""
    return SESSION_USER


@action(is_system_action=True)
async def get_turn_count() -> int:
    """
    Returns current turn count for the session.
    Placeholder — NeMo tracks this via conversation history length.
    """
    return 0  # NeMo enforces max_history_length from config.yml

# Write operations requiring explicit user confirmation
CONFIRMATION_REQUIRED = {
    "reset_password",
    "create_ticket",
    "update_ticket",
    "escalate_ticket",
    "close_ticket",
}

CONFIRMATION_PHRASES = [
    "yes, confirm", "yes confirm", "please proceed",
    "go ahead", "confirm", "yes please",
]


@action(is_system_action=True)
async def check_needs_confirmation(action_name: str) -> bool:
    """Returns True if this action requires explicit user confirmation."""
    return action_name in CONFIRMATION_REQUIRED


@action(is_system_action=True)
async def check_user_confirmed(action_name: str, user_message: str) -> bool:
    """
    Returns True if the user's message contains explicit confirmation.
    Residual gap: attacker who includes confirmation language in attack payload
    bypasses this gate. Documented as finding — addressed in Phase 5.
    """
    msg_lower = user_message.lower()
    confirmed = any(phrase in msg_lower for phrase in CONFIRMATION_PHRASES)
    if not confirmed:
        print(f"[authorization] CONFIRMATION MISSING for {action_name!r}")
    return confirmed
