import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for, make_response

app = Flask(__name__)
app.secret_key = "medicare-secret-key"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "medicare.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS login_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def build_dashboard(username):
    return {
        "orders": [
            {
                "name": "Paracetamol",
                "quantity": "2 packs",
                "dose": "500 mg",
                "status": "Ready",
            },
            {
                "name": "Vitamin D",
                "quantity": "1 bottle",
                "dose": "60 capsules",
                "status": "Processing",
            },
            {
                "name": "Antacid",
                "quantity": "1 pack",
                "dose": "20 tablets",
                "status": "Ready",
            },
        ],
        "status_steps": [
            {
                "title": "Order placed",
                "description": "We received your medicine request.",
                "state": "completed",
            },
            {
                "title": "Processing",
                "description": "Verifying prescription and preparing your order.",
                "state": "active",
            },
            {
                "title": "Payment",
                "description": "Your next payment is scheduled soon.",
                "state": "pending",
            },
            {
                "title": "Delivery",
                "description": "Your package will be dispatched shortly.",
                "state": "pending",
            },
        ],
        "payment": {
            "mode": "Card",
            "amount": "$24.50",
            "next_payment": "Today, 5:00 PM",
            "status": "Paid",
            "receipt": "RX-1024",
        },
        "delivery": {
            "address": "House No. 12, Green Park Road, Near City Pharmacy, Hyderabad.",
            "eta": "Today, 8:30 PM",
            "method": "Home delivery",
            "status": "On the way",
        },
    }


@app.before_request
def ensure_db():
    init_db()


@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        return render_template("login.html", error="Please enter both username and password."), 400

    password_hash = f"hash:{password}"
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.execute("INSERT INTO login_events (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()

    response = make_response(redirect(url_for("home")))
    response.set_cookie("username", username, httponly=True, samesite="Lax")
    return response


@app.route("/home")
def home():
    username = request.cookies.get("username", "").strip()
    if not username:
        return redirect(url_for("login_page"))

    conn = get_db()
    history = conn.execute(
        "SELECT username, logged_at FROM login_events WHERE username = ? ORDER BY id DESC LIMIT 5",
        (username,),
    ).fetchall()
    conn.close()

    dashboard = build_dashboard(username)
    return render_template(
        "home.html",
        username=username,
        history=history,
        dashboard=dashboard,
    )


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login_page")))
    response.set_cookie("username", "", expires=0)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
