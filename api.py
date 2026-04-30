import sqlite3
from flask import Blueprint, jsonify, request, abort, current_app

api = Blueprint("api", __name__, url_prefix="/api")
DB = "todos.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def todo_to_dict(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@api.get("/todos")
def list_todos():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    current_app.logger.info("api listed todos count=%d", len(rows))
    return jsonify([todo_to_dict(r) for r in rows])


@api.post("/todos")
def create_todo():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        abort(400, description="title is required")
    with get_db() as conn:
        cur = conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
        new_id = cur.lastrowid
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (new_id,)).fetchone()
    current_app.logger.info("api created todo id=%d title=%r", new_id, title)
    return jsonify(todo_to_dict(row)), 201


@api.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cur.rowcount == 0:
            abort(404, description=f"todo {todo_id} not found")
    current_app.logger.info("api deleted todo id=%d", todo_id)
    return "", 204
