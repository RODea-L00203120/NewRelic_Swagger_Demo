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
    """List all todos.
    ---
    tags:
      - todos
    responses:
      200:
        description: An array of todo objects, newest first.
        schema:
          type: array
          items:
            $ref: '#/definitions/Todo'
    definitions:
      Todo:
        type: object
        properties:
          id:
            type: integer
            example: 1
          title:
            type: string
            example: Buy milk
          done:
            type: boolean
            example: false
    """
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    current_app.logger.info("api listed todos count=%d", len(rows))
    return jsonify([todo_to_dict(r) for r in rows])


@api.post("/todos")
def create_todo():
    """Create a new todo.
    ---
    tags:
      - todos
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Buy milk
    responses:
      201:
        description: The created todo.
        schema:
          $ref: '#/definitions/Todo'
      400:
        description: title missing or empty.
    """
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
    """Delete a todo by id.
    ---
    tags:
      - todos
    parameters:
      - in: path
        name: todo_id
        required: true
        type: integer
        description: Numeric id of the todo to remove.
    responses:
      204:
        description: Deleted; no body.
      404:
        description: No todo with that id.
    """
    with get_db() as conn:
        cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cur.rowcount == 0:
            abort(404, description=f"todo {todo_id} not found")
    current_app.logger.info("api deleted todo id=%d", todo_id)
    return "", 204
