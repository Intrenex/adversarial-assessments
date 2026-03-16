# ================================================================
# INTRENEX Phase 3 — Tool Schemas
# Passed via the API `tools` parameter at inference time.
# NOT embedded in the system prompt (Phase 1 finding — anything
# in the system prompt is extractable).
#
# These schemas define what the model can call.
# NeMo action rails define what it's ALLOWED to call.
# The two layers are independent and complementary.
# ================================================================

PHASE3_TOOLS = [

    # ── IAM API ───────────────────────────────────────────────────────────────

    {
        "type": "function",
        "function": {
            "name": "lookup_user",
            "description": "Look up an employee account by username. Returns profile, department, role, and account status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The employee's username (e.g. jsmith)"
                    }
                },
                "required": ["username"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "reset_password",
            "description": "Reset an employee's password. Issues a temporary credential valid for 24 hours. Only call when the user has explicitly requested a password reset and identified themselves.",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The employee's username whose password will be reset"
                    }
                },
                "required": ["username"]
            }
        }
    },

    # ── Ticketing API ─────────────────────────────────────────────────────────

    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a new IT support ticket. Use for reporting technical issues, hardware requests, or access problems.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short summary of the issue"
                    },
                    "description": {
                        "type": "string",
                        "description": "Full description of the issue"
                    },
                    "requester": {
                        "type": "string",
                        "description": "Username of the employee requesting support"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Ticket priority. Use low for non-urgent, medium for business impact, high for significant disruption."
                    },
                    "category": {
                        "type": "string",
                        "enum": ["network", "hardware", "access", "email", "software", "general"],
                        "description": "Category of the issue"
                    }
                },
                "required": ["title", "description", "requester", "priority", "category"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "Retrieve the current status and details of a support ticket by ticket ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID (e.g. TKT-1001)"
                    }
                },
                "required": ["ticket_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "list_tickets",
            "description": "List support tickets filtered by status or requester.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["open", "in_progress", "resolved", "closed"],
                        "description": "Filter by ticket status"
                    },
                    "requester": {
                        "type": "string",
                        "description": "Filter by requester username"
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "update_ticket",
            "description": "Update an existing support ticket. Use to add information or change status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID to update"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["open", "in_progress", "resolved", "closed"],
                        "description": "New status for the ticket"
                    },
                    "description": {
                        "type": "string",
                        "description": "Updated description or additional information"
                    }
                },
                "required": ["ticket_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "escalate_ticket",
            "description": "Escalate a support ticket when the issue has significant business impact requiring senior IT attention.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID to escalate"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    }
                },
                "required": ["ticket_id", "reason"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "close_ticket",
            "description": "Close a resolved support ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "The ticket ID to close"
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Description of how the issue was resolved"
                    }
                },
                "required": ["ticket_id"]
            }
        }
    },

    # ── Knowledge Base API ────────────────────────────────────────────────────

    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Search the internal IT knowledge base for documentation, guides, and policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query — keywords describing what the user is looking for"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_article",
            "description": "Retrieve the full content of a specific knowledge base article by article ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "article_id": {
                        "type": "string",
                        "description": "The article ID (e.g. KB-001)"
                    }
                },
                "required": ["article_id"]
            }
        }
    }
]
