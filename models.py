"""
Model functions for FloatFry MRP.
All database queries are in this file to keep SQL out of routes.
Uses parameterised queries to prevent SQL injection.
"""

from database import get_db


# ── Machine functions ────────────────────────────────────────────────────────

def get_all_machines():
    """Return all machines ordered by name."""
    db = get_db()
    return db.execute(
        "SELECT * FROM machines ORDER BY name"
    ).fetchall()


def get_active_machines():
    """Return only machines with status 'Active'."""
    db = get_db()
    return db.execute(
        "SELECT * FROM machines WHERE status = 'Active' ORDER BY name"
    ).fetchall()


def get_machine(machine_id):
    """Return a single machine by ID."""
    db = get_db()
    return db.execute(
        "SELECT * FROM machines WHERE id = ?", (machine_id,)
    ).fetchone()


def create_machine(name, machine_type, status):
    """Insert a new machine and return its ID."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO machines (name, machine_type, status) VALUES (?, ?, ?)",
        (name, machine_type, status)
    )
    db.commit()
    return cursor.lastrowid


def update_machine(machine_id, name, machine_type, status):
    """Update an existing machine."""
    db = get_db()
    db.execute(
        "UPDATE machines SET name = ?, machine_type = ?, status = ? WHERE id = ?",
        (name, machine_type, status, machine_id)
    )
    db.commit()


def delete_machine(machine_id):
    """Delete a machine and its certifications."""
    db = get_db()
    db.execute("DELETE FROM certifications WHERE machine_id = ?", (machine_id,))
    db.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
    db.commit()


def count_active_orders_for_machine(machine_id):
    """Count work orders that are Pending or In Progress for a machine."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM work_orders "
        "WHERE machine_id = ? AND status IN ('Pending', 'In Progress')",
        (machine_id,)
    ).fetchone()
    return row["cnt"]


# ── Operator functions ───────────────────────────────────────────────────────

def get_all_operators():
    """Return all operators ordered by name."""
    db = get_db()
    return db.execute(
        "SELECT * FROM operators ORDER BY name"
    ).fetchall()


def get_operator(operator_id):
    """Return a single operator by ID."""
    db = get_db()
    return db.execute(
        "SELECT * FROM operators WHERE id = ?", (operator_id,)
    ).fetchone()


def employee_id_exists(employee_id, exclude_id=None):
    """Check if an employee_id is already in use."""
    db = get_db()
    if exclude_id:
        row = db.execute(
            "SELECT COUNT(*) as cnt FROM operators WHERE employee_id = ? AND id != ?",
            (employee_id, exclude_id)
        ).fetchone()
    else:
        row = db.execute(
            "SELECT COUNT(*) as cnt FROM operators WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()
    return row["cnt"] > 0


def create_operator(name, employee_id, contact):
    """Insert a new operator and return their ID."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO operators (name, employee_id, contact) VALUES (?, ?, ?)",
        (name, employee_id, contact)
    )
    db.commit()
    return cursor.lastrowid


def update_operator(operator_id, name, employee_id, contact):
    """Update an existing operator."""
    db = get_db()
    db.execute(
        "UPDATE operators SET name = ?, employee_id = ?, contact = ? WHERE id = ?",
        (name, employee_id, contact, operator_id)
    )
    db.commit()


def delete_operator(operator_id):
    """Delete an operator and their certifications."""
    db = get_db()
    db.execute("DELETE FROM certifications WHERE operator_id = ?", (operator_id,))
    db.execute("DELETE FROM operators WHERE id = ?", (operator_id,))
    db.commit()


def count_active_orders_for_operator(operator_id):
    """Count work orders that are Pending or In Progress for an operator."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM work_orders "
        "WHERE operator_id = ? AND status IN ('Pending', 'In Progress')",
        (operator_id,)
    ).fetchone()
    return row["cnt"]


# ── Certification functions ──────────────────────────────────────────────────

def get_certifications_for_operator(operator_id):
    """Return all machines an operator is certified for."""
    db = get_db()
    return db.execute(
        "SELECT c.id as cert_id, c.machine_id, m.name as machine_name, "
        "m.machine_type, c.certified_date "
        "FROM certifications c "
        "JOIN machines m ON c.machine_id = m.id "
        "WHERE c.operator_id = ? ORDER BY m.name",
        (operator_id,)
    ).fetchall()


def get_certified_operators(machine_id):
    """Return all operators certified for a given machine."""
    db = get_db()
    return db.execute(
        "SELECT o.id, o.name, o.employee_id "
        "FROM operators o "
        "JOIN certifications c ON o.id = c.operator_id "
        "WHERE c.machine_id = ? ORDER BY o.name",
        (machine_id,)
    ).fetchall()


def is_certified(operator_id, machine_id):
    """Check if an operator is certified for a specific machine. Returns True/False."""
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM certifications "
        "WHERE operator_id = ? AND machine_id = ?",
        (operator_id, machine_id)
    ).fetchone()
    return row["cnt"] > 0


def add_certification(operator_id, machine_id):
    """Add a certification record. Ignores duplicates."""
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO certifications (operator_id, machine_id) VALUES (?, ?)",
        (operator_id, machine_id)
    )
    db.commit()


def remove_certification(operator_id, machine_id):
    """Remove a specific certification."""
    db = get_db()
    db.execute(
        "DELETE FROM certifications WHERE operator_id = ? AND machine_id = ?",
        (operator_id, machine_id)
    )
    db.commit()


def remove_all_certifications(operator_id):
    """Remove all certifications for an operator (used when editing)."""
    db = get_db()
    db.execute(
        "DELETE FROM certifications WHERE operator_id = ?", (operator_id,)
    )
    db.commit()


# ── Work Order functions ─────────────────────────────────────────────────────

def get_all_work_orders(status_filter="All"):
    """Return work orders with machine and operator names, optionally filtered by status."""
    db = get_db()
    query = (
        "SELECT w.*, m.name as machine_name, o.name as operator_name "
        "FROM work_orders w "
        "JOIN machines m ON w.machine_id = m.id "
        "JOIN operators o ON w.operator_id = o.id "
    )
    if status_filter and status_filter != "All":
        query += " WHERE w.status = ? ORDER BY w.due_date ASC"
        return db.execute(query, (status_filter,)).fetchall()
    else:
        query += " ORDER BY w.due_date ASC"
        return db.execute(query).fetchall()


def get_work_order(order_id):
    """Return a single work order by ID."""
    db = get_db()
    return db.execute(
        "SELECT w.*, m.name as machine_name, o.name as operator_name "
        "FROM work_orders w "
        "JOIN machines m ON w.machine_id = m.id "
        "JOIN operators o ON w.operator_id = o.id "
        "WHERE w.id = ?",
        (order_id,)
    ).fetchone()


def get_recent_work_orders(limit=5):
    """Return the most recent work orders for the dashboard."""
    db = get_db()
    return db.execute(
        "SELECT w.*, m.name as machine_name, o.name as operator_name "
        "FROM work_orders w "
        "JOIN machines m ON w.machine_id = m.id "
        "JOIN operators o ON w.operator_id = o.id "
        "ORDER BY w.created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()


def create_work_order(product_name, quantity, priority, due_date, machine_id, operator_id):
    """Insert a new work order. Caller must validate certification first."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO work_orders (product_name, quantity, priority, due_date, "
        "machine_id, operator_id) VALUES (?, ?, ?, ?, ?, ?)",
        (product_name, quantity, priority, due_date, machine_id, operator_id)
    )
    db.commit()
    return cursor.lastrowid


def update_work_order(order_id, product_name, quantity, priority, due_date,
                      status, machine_id, operator_id):
    """Update an existing work order. Caller must validate certification first."""
    db = get_db()
    db.execute(
        "UPDATE work_orders SET product_name = ?, quantity = ?, priority = ?, "
        "due_date = ?, status = ?, machine_id = ?, operator_id = ? WHERE id = ?",
        (product_name, quantity, priority, due_date, status, machine_id,
         operator_id, order_id)
    )
    db.commit()


def update_work_order_status(order_id, status):
    """Update only the status of a work order."""
    db = get_db()
    db.execute(
        "UPDATE work_orders SET status = ? WHERE id = ?",
        (status, order_id)
    )
    db.commit()


def delete_work_order(order_id):
    """Delete a work order by ID."""
    db = get_db()
    db.execute("DELETE FROM work_orders WHERE id = ?", (order_id,))
    db.commit()


# ── Dashboard and Schedule ───────────────────────────────────────────────────

def get_dashboard_stats():
    """Return summary statistics for the dashboard."""
    db = get_db()
    stats = {}

    row = db.execute("SELECT COUNT(*) as cnt FROM machines").fetchone()
    stats["total_machines"] = row["cnt"]

    row = db.execute(
        "SELECT COUNT(*) as cnt FROM machines WHERE status = 'Active'"
    ).fetchone()
    stats["active_machines"] = row["cnt"]

    row = db.execute(
        "SELECT COUNT(*) as cnt FROM machines WHERE status = 'Under Maintenance'"
    ).fetchone()
    stats["maintenance_machines"] = row["cnt"]

    row = db.execute("SELECT COUNT(*) as cnt FROM operators").fetchone()
    stats["total_operators"] = row["cnt"]

    for s in ["Pending", "In Progress", "Completed"]:
        row = db.execute(
            "SELECT COUNT(*) as cnt FROM work_orders WHERE status = ?", (s,)
        ).fetchone()
        key = s.lower().replace(" ", "_") + "_orders"
        stats[key] = row["cnt"]

    row = db.execute("SELECT COUNT(*) as cnt FROM work_orders").fetchone()
    stats["total_orders"] = row["cnt"]

    return stats


def get_schedule(date_from="", date_to="", machine_filter=""):
    """Return work orders for the schedule view, with optional filters."""
    db = get_db()
    query = (
        "SELECT w.*, m.name as machine_name, o.name as operator_name "
        "FROM work_orders w "
        "JOIN machines m ON w.machine_id = m.id "
        "JOIN operators o ON w.operator_id = o.id "
        "WHERE 1=1 "
    )
    params = []

    if date_from:
        query += " AND w.due_date >= ? "
        params.append(date_from)
    if date_to:
        query += " AND w.due_date <= ? "
        params.append(date_to)
    if machine_filter:
        query += " AND w.machine_id = ? "
        params.append(int(machine_filter))

    query += " ORDER BY w.due_date ASC, m.name ASC"
    return db.execute(query, params).fetchall()
