import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "autoclaims.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claimant_name TEXT NOT NULL,
            claimant_email TEXT NOT NULL,
            claimant_phone TEXT,
            policy_number TEXT NOT NULL,
            claim_type TEXT NOT NULL,
            description TEXT NOT NULL,
            incident_date TEXT NOT NULL,
            location TEXT,
            estimated_loss REAL,
            image_paths TEXT DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'submitted',
            current_agent TEXT NOT NULL DEFAULT 'intake',
            intake_data TEXT,
            validation_data TEXT,
            assessment_data TEXT,
            review_gate_data TEXT,
            resolution_data TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_number TEXT UNIQUE NOT NULL,
            holder_name TEXT NOT NULL,
            holder_email TEXT NOT NULL,
            policy_type TEXT NOT NULL,
            coverage_amount REAL NOT NULL,
            deductible REAL NOT NULL,
            premium REAL NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS human_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            reviewer_notes TEXT,
            reviewed_by TEXT,
            reviewed_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (claim_id) REFERENCES claims(id)
        );
    """)

    seed_policies(cursor)
    conn.commit()
    conn.close()


def seed_policies(cursor):
    cursor.execute("SELECT COUNT(*) as count FROM policies")
    if cursor.fetchone()["count"] == 0:
        now = datetime.utcnow().isoformat()
        policies = [
            ("POL-2026-001", "Alice Johnson", "alice@email.com", "auto", 50000.0, 500.0, 1200.0, "2026-01-01", "2027-01-01", now),
            ("POL-2026-002", "Bob Smith", "bob@email.com", "home", 300000.0, 1000.0, 2400.0, "2026-02-01", "2027-02-01", now),
            ("POL-2026-003", "Carol Davis", "carol@email.com", "health", 100000.0, 250.0, 3600.0, "2026-03-01", "2027-03-01", now),
            ("POL-2026-004", "Daniel Lee", "daniel@email.com", "travel", 50000.0, 100.0, 300.0, "2026-04-01", "2027-04-01", now),
            ("POL-2026-005", "Eve Martinez", "eve@email.com", "property", 200000.0, 1500.0, 1800.0, "2026-05-01", "2027-05-01", now),
            ("POL-2026-006", "AutoClaims Corp", "corp@autoclaims.com", "liability", 1000000.0, 5000.0, 12000.0, "2026-01-01", "2027-01-01", now),
        ]
        cursor.executemany(
            "INSERT INTO policies (policy_number, holder_name, holder_email, policy_type, coverage_amount, deductible, premium, start_date, end_date, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            policies
        )


def save_claim(claim_data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    claim_data["created_at"] = now
    claim_data["updated_at"] = now

    fields = ["claimant_name", "claimant_email", "claimant_phone", "policy_number",
              "claim_type", "description", "incident_date", "location", "estimated_loss",
              "image_paths", "status", "current_agent", "created_at", "updated_at"]
    values = []
    for f in fields:
        v = claim_data.get(f)
        if f == "image_paths" and v is None:
            v = "[]"
        values.append(v)

    cursor.execute(
        "INSERT INTO claims (claimant_name, claimant_email, claimant_phone, policy_number, claim_type, description, incident_date, location, estimated_loss, image_paths, status, current_agent, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    claim_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return claim_id


def get_claim(claim_id: int) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_all_claims() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claims ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_claim(claim_id: int, data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    data["updated_at"] = datetime.utcnow().isoformat()
    set_parts = []
    values = []
    for key, val in data.items():
        if key != "id":
            if isinstance(val, dict):
                set_parts.append(f"{key} = ?")
                values.append(json.dumps(val))
            else:
                set_parts.append(f"{key} = ?")
                values.append(val)
    values.append(claim_id)
    cursor.execute(f"UPDATE claims SET {', '.join(set_parts)} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_policy(policy_number: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policies WHERE policy_number = ?", (policy_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_human_review(claim_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "INSERT INTO human_reviews (claim_id, status, created_at) VALUES (?, 'pending', ?)",
        (claim_id, now)
    )
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return review_id


def get_pending_reviews() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hr.*, c.claimant_name, c.claim_type, c.status as claim_status, c.assessment_data
        FROM human_reviews hr
        JOIN claims c ON c.id = hr.claim_id
        WHERE hr.status = 'pending'
        ORDER BY hr.created_at ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_human_review(review_id: int, status: str, notes: str, reviewer: str):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        "UPDATE human_reviews SET status = ?, reviewer_notes = ?, reviewed_by = ?, reviewed_at = ? WHERE id = ?",
        (status, notes, reviewer, now, review_id)
    )
    conn.commit()
    conn.close()
