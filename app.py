from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from db import init_db, get_conn
from risk_engine import risk_score_engine
import csv
import io

app = Flask(__name__)
app.secret_key = "dev-secret-change-this"

# ✅ Initialize database (Flask 3 compatible)
init_db()


# ------------------------------
# Helper Functions
# ------------------------------

def fetch_projects():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def fetch_project(project_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    conn.close()
    return row


def fetch_metrics(project_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM metrics
        WHERE project_id=?
        ORDER BY snapshot_date ASC, id ASC
    """, (project_id,)).fetchall()
    conn.close()
    return rows


def fetch_latest_two_metrics(project_id):
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM metrics
        WHERE project_id=?
        ORDER BY snapshot_date DESC, id DESC
        LIMIT 2
    """, (project_id,)).fetchall()
    conn.close()
    return rows


# ------------------------------
# Routes
# ------------------------------

@app.route("/")
def index():
    projects = fetch_projects()
    cards = []

    for p in projects:
        latest_two = fetch_latest_two_metrics(p["id"])
        latest = latest_two[0] if len(latest_two) > 0 else None
        prev = latest_two[1] if len(latest_two) > 1 else None

        if latest:
            risk = risk_score_engine(latest, prev)
            cards.append({"project": p, "risk": risk, "latest": latest})
        else:
            cards.append({"project": p, "risk": None, "latest": None})

    return render_template("index.html", cards=cards)


@app.route("/projects/new", methods=["GET", "POST"])
def project_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        owner = request.form.get("owner", "").strip()
        start_date = request.form.get("start_date", "").strip()
        end_date = request.form.get("end_date", "").strip()

        if not all([name, owner, start_date, end_date]):
            flash("All fields are required.", "danger")
            return render_template("project_new.html")

        conn = get_conn()
        conn.execute("""
            INSERT INTO projects (name, owner, start_date, end_date)
            VALUES (?, ?, ?, ?)
        """, (name, owner, start_date, end_date))
        conn.commit()
        conn.close()

        flash("Project created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("project_new.html")


@app.route("/projects/<int:project_id>")
def project_view(project_id):
    project = fetch_project(project_id)
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("index"))

    metrics = fetch_metrics(project_id)

    risk_points = []
    for i, m in enumerate(metrics):
        prev = metrics[i - 1] if i > 0 else None
        r = risk_score_engine(m, prev)
        risk_points.append({"metric": m, "risk": r})

    latest = risk_points[-1] if risk_points else None

    dates = [rp["metric"]["snapshot_date"] for rp in risk_points]
    risk_scores = [rp["risk"].risk_score for rp in risk_points]
    completion_rates = [
        rp["risk"].kpis["completion_rate"] * 100 for rp in risk_points
    ]

    return render_template(
        "project_view.html",
        project=project,
        risk_points=risk_points,
        latest=latest,
        dates=dates,
        risk_scores=risk_scores,
        completion_rates=completion_rates
    )


@app.route("/projects/<int:project_id>/metrics/add", methods=["GET", "POST"])
def metric_add(project_id):
    project = fetch_project(project_id)
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            conn = get_conn()
            conn.execute("""
                INSERT INTO metrics (
                    project_id, snapshot_date,
                    planned_tasks, completed_tasks, in_progress_tasks,
                    blockers_count, bugs_open, scope_change_percent,
                    avg_cycle_time_days, comments
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                request.form["snapshot_date"],
                int(request.form["planned_tasks"]),
                int(request.form["completed_tasks"]),
                int(request.form["in_progress_tasks"]),
                int(request.form["blockers_count"]),
                int(request.form["bugs_open"]),
                float(request.form["scope_change_percent"]),
                float(request.form["avg_cycle_time_days"]),
                request.form.get("comments", "")
            ))
            conn.commit()
            conn.close()

            flash("Metrics added successfully!", "success")
            return redirect(url_for("project_view", project_id=project_id))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for("metric_add", project_id=project_id))

    return render_template("metric_add.html", project=project, form={})


@app.route("/projects/<int:project_id>/report")
def report(project_id):
    project = fetch_project(project_id)
    metrics = fetch_metrics(project_id)

    rows = []
    for i, m in enumerate(metrics):
        prev = metrics[i - 1] if i > 0 else None
        r = risk_score_engine(m, prev)
        rows.append((m, r))

    return render_template("report.html", project=project, rows=rows)


@app.route("/projects/<int:project_id>/report.csv")
def report_csv(project_id):
    project = fetch_project(project_id)
    metrics = fetch_metrics(project_id)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Date", "Planned", "Completed", "Risk Score", "Risk Level"
    ])

    for i, m in enumerate(metrics):
        prev = metrics[i - 1] if i > 0 else None
        r = risk_score_engine(m, prev)

        writer.writerow([
            m["snapshot_date"],
            m["planned_tasks"],
            m["completed_tasks"],
            r.risk_score,
            r.risk_level
        ])

    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)

    filename = f"{project['name'].replace(' ', '_')}_report.csv"
    return send_file(mem, mimetype="text/csv",
                     as_attachment=True,
                     download_name=filename)


# ------------------------------
# Run App
# ------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)