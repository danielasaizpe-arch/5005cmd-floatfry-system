"""
Seed data for FloatFry MRP.
Run this script once to populate the database with sample data for testing.
Usage: python seed_data.py
"""

import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "floatfry.db")


def seed():
    """Insert sample machines, operators, certifications, and work orders."""
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")

    # ── Machines ─────────────────────────────────────────────────────────
    machines = [
        ("Stamping Press A1", "Stamping Press", "Active"),
        ("Stamping Press A2", "Stamping Press", "Active"),
        ("CNC Lathe B1", "CNC Lathe", "Active"),
        ("Polishing Unit C1", "Polishing Unit", "Active"),
        ("Coating Line D1", "Coating Line", "Under Maintenance"),
        ("Assembly Station E1", "Assembly Station", "Active"),
    ]
    db.executemany(
        "INSERT OR IGNORE INTO machines (name, machine_type, status) VALUES (?, ?, ?)",
        machines
    )

    # ── Operators ────────────────────────────────────────────────────────
    operators = [
        ("James Carter", "EMP-001", "j.carter@floatfry.com"),
        ("Sarah Mitchell", "EMP-002", "s.mitchell@floatfry.com"),
        ("David Okonkwo", "EMP-003", "d.okonkwo@floatfry.com"),
        ("Emily Zhang", "EMP-004", "e.zhang@floatfry.com"),
        ("Robert Singh", "EMP-005", "r.singh@floatfry.com"),
    ]
    for name, emp_id, contact in operators:
        try:
            db.execute(
                "INSERT INTO operators (name, employee_id, contact) VALUES (?, ?, ?)",
                (name, emp_id, contact)
            )
        except sqlite3.IntegrityError:
            pass  # Skip if already exists

    # ── Certifications ───────────────────────────────────────────────────
    # (operator_id, machine_id) — based on insert order above
    certifications = [
        (1, 1), (1, 2), (1, 6),       # James: both stamping presses + assembly
        (2, 1), (2, 3), (2, 4),       # Sarah: stamping A1 + CNC + polishing
        (3, 2), (3, 5), (3, 6),       # David: stamping A2 + coating + assembly
        (4, 3), (4, 4),               # Emily: CNC + polishing
        (5, 1), (5, 5), (5, 6),       # Robert: stamping A1 + coating + assembly
    ]
    for op_id, m_id in certifications:
        try:
            db.execute(
                "INSERT INTO certifications (operator_id, machine_id) VALUES (?, ?)",
                (op_id, m_id)
            )
        except sqlite3.IntegrityError:
            pass

    # ── Work Orders ──────────────────────────────────────────────────────
    work_orders = [
        ("Premium Cast Iron Skillet", 200, "High", "Pending", "2026-04-14", 1, 1),
        ("Stainless Steel Saucepan", 150, "Medium", "In Progress", "2026-04-12", 3, 4),
        ("Non-stick Frying Pan", 300, "High", "Pending", "2026-04-15", 2, 3),
        ("Copper Bottom Stockpot", 100, "Low", "Completed", "2026-04-10", 4, 2),
        ("Enamel Dutch Oven", 80, "Medium", "In Progress", "2026-04-13", 6, 1),
        ("Wok with Lid", 250, "High", "Pending", "2026-04-16", 1, 5),
    ]
    for product, qty, priority, status, due, m_id, op_id in work_orders:
        try:
            db.execute(
                "INSERT INTO work_orders (product_name, quantity, priority, status, "
                "due_date, machine_id, operator_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (product, qty, priority, status, due, m_id, op_id)
            )
        except sqlite3.IntegrityError:
            pass

    db.commit()
    db.close()
    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed()
