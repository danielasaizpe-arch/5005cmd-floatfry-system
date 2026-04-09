# FloatFry — Production Scheduling and Resource Allocation System

## About

This is a web-based MVP for FloatFry, a cookware and kitchen products manufacturer.
It helps the production team manage machines, operators, certifications, and work orders.

Built for the module **5005CMD Software Engineering** at Coventry University.

## Technology Stack

- Python 3
- Flask (web framework)
- SQLite (database)
- Jinja2 templates (HTML rendering)
- HTML / CSS

## How to Run

1. Make sure Python 3 or higher is installed on your computer.

2. Open a terminal and navigate to the project folder:
   ```
   cd floatfry
   ```

3. (Optional) Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate        # Mac/Linux
   venv\Scripts\activate           # Windows
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Open a web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## Loading Sample Data

To add some sample machines, operators, and work orders for testing:

```
python seed_data.py
```

This only needs to be run once. The database file `floatfry.db` will be created automatically.

## Project Structure

```
floatfry/
  app.py               - Main Flask application and routes
  models.py            - Database query functions
  database.py          - Database connection helper
  schema.sql           - Table creation script
  seed_data.py         - Sample data for testing
  floatfry.db          - SQLite database (created at runtime)
  requirements.txt     - Python dependencies
  README.md            - This file
  static/
    css/
      style.css        - Stylesheet
  templates/
    base.html          - Base layout
    dashboard.html     - Dashboard page
    machines.html      - Machine list
    add_machine.html   - Add/edit machine form
    operators.html     - Operator list
    add_operator.html  - Add/edit operator form
    work_orders.html   - Work order list
    add_work_order.html - Add/edit work order form
    schedule.html      - Schedule view
```

## Features

- Machine management (add, edit, delete)
- Operator management (add, edit, delete)
- Certification tracking (which operators can use which machines)
- Work order management with assignment to machines and operators
- Certification validation (prevents uncertified assignments)
- Dashboard with summary statistics
- Schedule view with date and machine filters
