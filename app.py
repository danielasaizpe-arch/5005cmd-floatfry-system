"""
FloatFry Production Scheduling and Resource Allocation System
Main Flask application file.
5005CMD Software Engineering - Coventry University
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db, close_db, init_db
import models

app = Flask(__name__)
app.secret_key = "floatfry-dev-key"

# Close database connection after each request
app.teardown_appcontext(close_db)


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """Home page showing summary statistics."""
    stats = models.get_dashboard_stats()
    recent_orders = models.get_recent_work_orders(limit=5)
    return render_template("dashboard.html", stats=stats, recent_orders=recent_orders)


# ── Machines ─────────────────────────────────────────────────────────────────

@app.route("/machines")
def machines():
    """List all machines."""
    all_machines = models.get_all_machines()
    return render_template("machines.html", machines=all_machines)


@app.route("/machines/add", methods=["GET", "POST"])
def add_machine():
    """Add a new machine."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        machine_type = request.form.get("machine_type", "").strip()
        status = request.form.get("status", "Active")

        # Validate required fields
        if not name or not machine_type:
            flash("Machine name and type are required.", "error")
            return render_template("add_machine.html",
                                   name=name, machine_type=machine_type, status=status)

        models.create_machine(name, machine_type, status)
        flash("Machine added successfully.", "success")
        return redirect(url_for("machines"))

    return render_template("add_machine.html")


@app.route("/machines/<int:machine_id>/edit", methods=["GET", "POST"])
def edit_machine(machine_id):
    """Edit an existing machine."""
    machine = models.get_machine(machine_id)
    if not machine:
        flash("Machine not found.", "error")
        return redirect(url_for("machines"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        machine_type = request.form.get("machine_type", "").strip()
        status = request.form.get("status", "Active")

        if not name or not machine_type:
            flash("Machine name and type are required.", "error")
            return render_template("add_machine.html", editing=True, machine=machine,
                                   name=name, machine_type=machine_type, status=status)

        models.update_machine(machine_id, name, machine_type, status)
        flash("Machine updated successfully.", "success")
        return redirect(url_for("machines"))

    return render_template("add_machine.html", editing=True, machine=machine,
                           name=machine["name"], machine_type=machine["machine_type"],
                           status=machine["status"])


@app.route("/machines/<int:machine_id>/delete", methods=["POST"])
def delete_machine(machine_id):
    """Delete a machine if it has no active work orders."""
    active = models.count_active_orders_for_machine(machine_id)
    if active > 0:
        flash("Cannot delete this machine. It has active work orders.", "error")
    else:
        models.delete_machine(machine_id)
        flash("Machine deleted.", "success")
    return redirect(url_for("machines"))


# ── Operators ────────────────────────────────────────────────────────────────

@app.route("/operators")
def operators():
    """List all operators."""
    all_operators = models.get_all_operators()
    return render_template("operators.html", operators=all_operators)


@app.route("/operators/add", methods=["GET", "POST"])
def add_operator():
    """Add a new operator."""
    machines_list = models.get_all_machines()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        employee_id = request.form.get("employee_id", "").strip()
        contact = request.form.get("contact", "").strip()
        cert_ids = request.form.getlist("certifications")

        if not name or not employee_id:
            flash("Operator name and employee ID are required.", "error")
            return render_template("add_operator.html", machines=machines_list,
                                   name=name, employee_id=employee_id, contact=contact,
                                   selected_certs=cert_ids)

        # Check if employee_id already exists
        if models.employee_id_exists(employee_id):
            flash("An operator with this Employee ID already exists.", "error")
            return render_template("add_operator.html", machines=machines_list,
                                   name=name, employee_id=employee_id, contact=contact,
                                   selected_certs=cert_ids)

        operator_id = models.create_operator(name, employee_id, contact)

        # Add certifications
        for mid in cert_ids:
            models.add_certification(operator_id, int(mid))

        flash("Operator added successfully.", "success")
        return redirect(url_for("operators"))

    return render_template("add_operator.html", machines=machines_list)


@app.route("/operators/<int:operator_id>/edit", methods=["GET", "POST"])
def edit_operator(operator_id):
    """Edit an existing operator and their certifications."""
    operator = models.get_operator(operator_id)
    if not operator:
        flash("Operator not found.", "error")
        return redirect(url_for("operators"))

    machines_list = models.get_all_machines()
    current_certs = models.get_certifications_for_operator(operator_id)
    current_cert_ids = [str(c["machine_id"]) for c in current_certs]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        employee_id = request.form.get("employee_id", "").strip()
        contact = request.form.get("contact", "").strip()
        cert_ids = request.form.getlist("certifications")

        if not name or not employee_id:
            flash("Operator name and employee ID are required.", "error")
            return render_template("add_operator.html", editing=True, operator=operator,
                                   machines=machines_list, name=name,
                                   employee_id=employee_id, contact=contact,
                                   selected_certs=cert_ids)

        # Check employee_id uniqueness (exclude current operator)
        if models.employee_id_exists(employee_id, exclude_id=operator_id):
            flash("An operator with this Employee ID already exists.", "error")
            return render_template("add_operator.html", editing=True, operator=operator,
                                   machines=machines_list, name=name,
                                   employee_id=employee_id, contact=contact,
                                   selected_certs=cert_ids)

        models.update_operator(operator_id, name, employee_id, contact)

        # Update certifications: remove old, add new
        models.remove_all_certifications(operator_id)
        for mid in cert_ids:
            models.add_certification(operator_id, int(mid))

        flash("Operator updated successfully.", "success")
        return redirect(url_for("operators"))

    return render_template("add_operator.html", editing=True, operator=operator,
                           machines=machines_list, name=operator["name"],
                           employee_id=operator["employee_id"],
                           contact=operator["contact"],
                           selected_certs=current_cert_ids)


@app.route("/operators/<int:operator_id>/delete", methods=["POST"])
def delete_operator(operator_id):
    """Delete an operator if they have no active work orders."""
    active = models.count_active_orders_for_operator(operator_id)
    if active > 0:
        flash("Cannot delete this operator. They have active work orders.", "error")
    else:
        models.delete_operator(operator_id)
        flash("Operator deleted.", "success")
    return redirect(url_for("operators"))


# ── Work Orders ──────────────────────────────────────────────────────────────

@app.route("/workorders")
def work_orders():
    """List all work orders, with optional status filter."""
    status_filter = request.args.get("status", "All")
    all_orders = models.get_all_work_orders(status_filter)
    return render_template("work_orders.html", orders=all_orders, current_filter=status_filter)


@app.route("/workorders/add", methods=["GET", "POST"])
def add_work_order():
    """Create a new work order."""
    machines_list = models.get_active_machines()
    operators_list = models.get_all_operators()

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        quantity = request.form.get("quantity", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "").strip()
        machine_id = request.form.get("machine_id", "")
        operator_id = request.form.get("operator_id", "")

        # Basic validation
        errors = []
        if not product_name:
            errors.append("Product name is required.")
        if not quantity or not quantity.isdigit() or int(quantity) <= 0:
            errors.append("Quantity must be a positive number.")
        if not due_date:
            errors.append("Due date is required.")
        if not machine_id:
            errors.append("Please select a machine.")
        if not operator_id:
            errors.append("Please select an operator.")

        # CRITICAL: Certification validation
        if machine_id and operator_id:
            if not models.is_certified(int(operator_id), int(machine_id)):
                errors.append(
                    "This operator is NOT certified for the selected machine. "
                    "Assignment rejected."
                )

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("add_work_order.html",
                                   machines=machines_list, operators=operators_list,
                                   product_name=product_name, quantity=quantity,
                                   priority=priority, due_date=due_date,
                                   machine_id=machine_id, operator_id=operator_id)

        models.create_work_order(
            product_name, int(quantity), priority, due_date,
            int(machine_id), int(operator_id)
        )
        flash("Work order created successfully.", "success")
        return redirect(url_for("work_orders"))

    return render_template("add_work_order.html",
                           machines=machines_list, operators=operators_list)


@app.route("/workorders/<int:order_id>/edit", methods=["GET", "POST"])
def edit_work_order(order_id):
    """Edit an existing work order."""
    order = models.get_work_order(order_id)
    if not order:
        flash("Work order not found.", "error")
        return redirect(url_for("work_orders"))

    machines_list = models.get_active_machines()
    operators_list = models.get_all_operators()

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        quantity = request.form.get("quantity", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "Pending")
        machine_id = request.form.get("machine_id", "")
        operator_id = request.form.get("operator_id", "")

        errors = []
        if not product_name:
            errors.append("Product name is required.")
        if not quantity or not quantity.isdigit() or int(quantity) <= 0:
            errors.append("Quantity must be a positive number.")
        if not due_date:
            errors.append("Due date is required.")
        if not machine_id:
            errors.append("Please select a machine.")
        if not operator_id:
            errors.append("Please select an operator.")

        # CRITICAL: Certification validation
        if machine_id and operator_id:
            if not models.is_certified(int(operator_id), int(machine_id)):
                errors.append(
                    "This operator is NOT certified for the selected machine. "
                    "Assignment rejected."
                )

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("add_work_order.html", editing=True, order=order,
                                   machines=machines_list, operators=operators_list,
                                   product_name=product_name, quantity=quantity,
                                   priority=priority, due_date=due_date,
                                   status=status,
                                   machine_id=machine_id, operator_id=operator_id)

        models.update_work_order(
            order_id, product_name, int(quantity), priority,
            due_date, status, int(machine_id), int(operator_id)
        )
        flash("Work order updated successfully.", "success")
        return redirect(url_for("work_orders"))

    return render_template("add_work_order.html", editing=True, order=order,
                           machines=machines_list, operators=operators_list,
                           product_name=order["product_name"],
                           quantity=order["quantity"],
                           priority=order["priority"],
                           due_date=order["due_date"],
                           status=order["status"],
                           machine_id=str(order["machine_id"]),
                           operator_id=str(order["operator_id"]))


@app.route("/workorders/<int:order_id>/status", methods=["POST"])
def update_status(order_id):
    """Quick-update work order status."""
    new_status = request.form.get("status", "Pending")
    models.update_work_order_status(order_id, new_status)
    flash(f"Work order status changed to {new_status}.", "success")
    return redirect(url_for("work_orders"))


@app.route("/workorders/<int:order_id>/delete", methods=["POST"])
def delete_work_order(order_id):
    """Delete a work order."""
    models.delete_work_order(order_id)
    flash("Work order deleted.", "success")
    return redirect(url_for("work_orders"))


# ── Schedule ─────────────────────────────────────────────────────────────────

@app.route("/schedule")
def schedule():
    """Show schedule view with optional date and machine filters."""
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    machine_filter = request.args.get("machine_id", "")

    machines_list = models.get_all_machines()
    schedule_data = models.get_schedule(date_from, date_to, machine_filter)

    return render_template("schedule.html",
                           schedule=schedule_data,
                           machines=machines_list,
                           date_from=date_from,
                           date_to=date_to,
                           machine_id=machine_filter)


# ── API helper for certification check (optional JS enhancement) ─────────

@app.route("/api/certified-operators/<int:machine_id>")
def api_certified_operators(machine_id):
    """Return JSON list of operators certified for a given machine."""
    operators = models.get_certified_operators(machine_id)
    result = [{"id": op["id"], "name": op["name"],
               "employee_id": op["employee_id"]} for op in operators]
    from flask import jsonify
    return jsonify(result)


# ── Run the app ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, port=5000)
