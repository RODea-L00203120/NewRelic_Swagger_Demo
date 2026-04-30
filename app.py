import logging
import sqlite3
from flask import Flask, request, redirect, render_template, url_for

from api import api as api_blueprint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.register_blueprint(api_blueprint)
DB = "todos.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )"""
        )


@app.route("/")
def index():
    with get_db() as conn:
        todos = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    app.logger.info("listed todos count=%d", len(todos))
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = (request.form.get("title") or "").strip()
    if not title:
        app.logger.warning("rejected empty todo title")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    app.logger.info("added todo title=%r", title)
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    with get_db() as conn:
        conn.execute("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
    app.logger.info("toggled todo id=%d", todo_id)
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    app.logger.info("deleted todo id=%d", todo_id)
    return redirect(url_for("index"))


@app.route("/errortrigger")
def errortrigger():
    app.logger.error("errortrigger invoked — raising deliberate exception")
    raise RuntimeError("Deliberate error for alert-condition demonstration")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
