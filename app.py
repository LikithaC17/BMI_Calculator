import os
import sqlite3
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "bmi_secret_key"

DATABASE = os.path.join(app.root_path, "bmi_data.db")


def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the bmi_records table if it does not exist yet."""
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bmi_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            category TEXT NOT NULL,
            date_time TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_bmi_record(weight, height_cm, bmi_value, category):
    """Store one BMI calculation in the database."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO bmi_records (weight, height, bmi, category, date_time) VALUES (?, ?, ?, ?, ?)",
        (weight, height_cm, bmi_value, category, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_bmi_history():
    """Fetch all saved BMI records from the database."""
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM bmi_records ORDER BY id DESC").fetchall()
    conn.close()
    return records


with app.app_context():
    init_db()


@app.route("/clear", methods=["GET"])
def clear_session():
    """Clear the temporary result data and return to the calculator page."""
    session.clear()
    return redirect(url_for("bmi"))


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    """Delete one BMI record from the SQLite database."""
    conn = get_db_connection()
    conn.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    flash("BMI record deleted successfully.", "success")
    return redirect(url_for("bmi"))


@app.route("/delete_all", methods=["POST"])
def delete_all_history():
    """Delete all BMI history records from the SQLite database."""
    conn = get_db_connection()
    conn.execute("DELETE FROM bmi_records")
    conn.commit()
    conn.close()
    flash("All BMI history has been deleted.", "success")
    return redirect(url_for("bmi"))


@app.route("/", methods=["GET", "POST"])
def bmi():
    """Calculate BMI, store it in the database, and show the latest results."""
    history = get_bmi_history()

    if request.method == "POST":
        weight = float(request.form["weight"])
        height_cm = float(request.form["height"])
        height_m = height_cm / 100

        bmi_value = round(weight / (height_m ** 2), 2)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 24.9:
            category = "Normal weight"
        elif bmi_value < 29.9:
            category = "Overweight"
        else:
            category = "Obese"

        # Save values in session for quick display on the page
        session["weight"] = weight
        session["height"] = height_cm
        session["bmi"] = bmi_value
        session["category"] = category

        # Save the calculation permanently in the SQLite database
        save_bmi_record(weight, height_cm, bmi_value, category)
        history = get_bmi_history()

    return render_template(
        "index.html",
        weight=session.get("weight"),
        height=session.get("height"),
        bmi=session.get("bmi"),
        category=session.get("category"),
        history=history,
    )


if __name__ == "__main__":
    app.run(debug=True)


