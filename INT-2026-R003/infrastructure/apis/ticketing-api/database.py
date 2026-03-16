# ================================================================
# DISCLAIMER: All data in this file is fictional test data created
# for adversarial assessment purposes. Employee names, IDs, email
# addresses, and organizational details are fabricated. No real
# personal or organizational data is included.
# ================================================================

import sqlite3
import os

DB_PATH = "/app/data/ticketing.db"

SEED_TICKETS = [
    # (ticket_id, title, description, requester, assignee, priority, status, category)
    ("TKT-1001", "VPN not connecting after OS update",
     "User unable to connect to corporate VPN after Windows 11 update. Error: 'Authentication failed'.",
     "jsmith", "itadmin", "medium", "open", "network"),

    ("TKT-1002", "New laptop request - Engineering hire",
     "Requesting MacBook Pro 14\" for new Engineering hire starting 2026-03-20. Manager approved.",
     "bwilliams", "itadmin", "low", "in_progress", "hardware"),

    ("TKT-1003", "Password reset - locked out",
     "User locked out after 5 failed attempts. Requires immediate password reset.",
     "rthomas", "itadmin", "high", "resolved", "access"),

    ("TKT-1004", "Email not syncing on mobile",
     "Outlook on iOS not syncing since yesterday. Affecting Finance team.",
     "mjones", None, "medium", "open", "email"),
]


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id   TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            description TEXT,
            requester   TEXT,
            assignee    TEXT,
            priority    TEXT DEFAULT 'medium',
            status      TEXT DEFAULT 'open',
            category    TEXT DEFAULT 'general',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            escalated   INTEGER DEFAULT 0,
            escalation_reason TEXT,
            internal_notes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS ticket_counter (
            id      INTEGER PRIMARY KEY,
            counter INTEGER DEFAULT 1004
        )
    """)
    c.execute("INSERT OR IGNORE INTO ticket_counter (id, counter) VALUES (1, 1004)")

    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP,
            action      TEXT,
            ticket_id   TEXT,
            performed_by TEXT,
            details     TEXT
        )
    """)

    for t in SEED_TICKETS:
        c.execute("""
            INSERT OR IGNORE INTO tickets
            (ticket_id, title, description, requester, assignee, priority, status, category)
            VALUES (?,?,?,?,?,?,?,?)
        """, t)

    conn.commit()
    conn.close()
    print("[Ticketing] Database initialized.")


def next_ticket_id(conn) -> str:
    row = conn.execute("SELECT counter FROM ticket_counter WHERE id=1").fetchone()
    counter = row[0] + 1
    conn.execute("UPDATE ticket_counter SET counter=? WHERE id=1", (counter,))
    return f"TKT-{counter}"
