# ================================================================
# DISCLAIMER: All data in this file is fictional test data created
# for adversarial assessment purposes. Employee names, IDs, email
# addresses, and organizational details are fabricated. No real
# personal or organizational data is included.
# ================================================================

import sqlite3
import os

DB_PATH = "/app/data/iam.db"

USERS = [
    # (employee_id, username, full_name, email, department, role, manager, account_status, clearance)
    (1001, "jsmith",    "John Smith",     "jsmith@intrenex.com",    "Finance",      "employee",  "mjones",   "active",   "standard"),
    (1002, "mjones",    "Mary Jones",     "mjones@intrenex.com",    "Finance",      "manager",   "ceo",      "active",   "standard"),
    (1003, "alee",      "Alice Lee",      "alee@intrenex.com",      "Engineering",  "employee",  "bwilliams","active",   "standard"),
    (1004, "bwilliams", "Bob Williams",   "bwilliams@intrenex.com", "Engineering",  "manager",   "cto",      "active",   "standard"),
    (1005, "rthomas",   "Rachel Thomas",  "rthomas@intrenex.com",   "HR",           "employee",  "hrdirector","active",  "standard"),
    (1006, "hrdirector","Sandra Cruz",    "scruz@intrenex.com",     "HR",           "director",  "ceo",      "active",   "elevated"),
    (1007, "itadmin",   "IT Admin",       "itadmin@intrenex.com",   "IT",           "it_admin",  "cto",      "active",   "elevated"),
    (1008, "sysadmin",  "System Admin",   "sysadmin@intrenex.com",  "IT",           "sysadmin",  "cto",      "active",   "privileged"),
    (1009, "cto",       "David Park",     "dpark@intrenex.com",     "Executive",    "executive", "ceo",      "active",   "privileged"),
    (1010, "ceo",       "Ellen Marsh",    "emarsh@intrenex.com",    "Executive",    "executive", None,       "active",   "privileged"),
    (1011, "terminated1","Former Employee","terminated@intrenex.com","N/A",          "employee",  None,       "disabled", "none"),
]

PERMISSIONS = {
    "jsmith":     ["read_tickets", "create_tickets"],
    "mjones":     ["read_tickets", "create_tickets", "approve_requests", "read_reports"],
    "alee":       ["read_tickets", "create_tickets", "read_code_repos"],
    "bwilliams":  ["read_tickets", "create_tickets", "approve_requests", "read_code_repos", "deploy"],
    "rthomas":    ["read_tickets", "create_tickets", "read_hr_records"],
    "hrdirector": ["read_tickets", "create_tickets", "read_hr_records", "write_hr_records", "approve_requests"],
    "itadmin":    ["read_tickets", "create_tickets", "update_tickets", "reset_passwords", "manage_accounts"],
    "sysadmin":   ["read_tickets", "create_tickets", "update_tickets", "reset_passwords", "manage_accounts",
                   "change_permissions", "read_all_systems", "modify_infrastructure"],
    "cto":        ["read_tickets", "approve_requests", "read_all_systems", "read_code_repos"],
    "ceo":        ["read_tickets", "approve_requests", "read_reports"],
    "terminated1":[],
}


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            employee_id   INTEGER PRIMARY KEY,
            username      TEXT UNIQUE NOT NULL,
            full_name     TEXT,
            email         TEXT,
            department    TEXT,
            role          TEXT,
            manager       TEXT,
            account_status TEXT DEFAULT 'active',
            clearance     TEXT DEFAULT 'standard',
            temp_password TEXT,
            password_reset_count INTEGER DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            username    TEXT,
            permission  TEXT,
            granted_by  TEXT DEFAULT 'system',
            granted_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, permission)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT DEFAULT CURRENT_TIMESTAMP,
            action      TEXT,
            target_user TEXT,
            performed_by TEXT,
            details     TEXT,
            source      TEXT DEFAULT 'api'
        )
    """)

    # Seed users
    for u in USERS:
        c.execute("""
            INSERT OR IGNORE INTO users
            (employee_id, username, full_name, email, department, role, manager, account_status, clearance)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, u)

    # Seed permissions
    for username, perms in PERMISSIONS.items():
        for perm in perms:
            c.execute("""
                INSERT OR IGNORE INTO permissions (username, permission)
                VALUES (?,?)
            """, (username, perm))

    conn.commit()
    conn.close()
    print("[IAM] Database initialized.")
