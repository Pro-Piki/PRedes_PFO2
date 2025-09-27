from flask import Flask, request, jsonify, Response, render_template, g
from flask_bcrypt import Bcrypt
import sqlite3
import base64
import os
from functools import wraps

DB_USERS = "data.db"
DB_TASKS = "tasks.db"

app = Flask(__name__, template_folder="templates", static_folder="static")
bcrypt = Bcrypt(app)

# ------------------- DB helpers -------------------
def get_db(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db(DB_USERS)
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)
    db.commit()
    db.close()

def init_tasks_db():
    db = get_db(DB_TASKS)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            usuario TEXT NOT NULL
        );
    """)
    db.commit()
    db.close()

# ------------------- Utility -------------------
def user_by_username(username):
    db = get_db(DB_USERS)
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    db.close()
    return user

# ------------------- Basic Auth -------------------
def require_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return Response('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        try:
            b64 = auth_header.split(" ", 1)[1]
            decoded = base64.b64decode(b64).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            return Response('Invalid auth header', 400)
        user = user_by_username(username)
        if user is None or not bcrypt.check_password_hash(user["password_hash"], password):
            return Response('Invalid credentials', 401)
        return f(username, *args, **kwargs)  # pasamos username al endpoint
    return decorated

# ------------------- Endpoints -------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/registro", methods=["POST"])
def registro():
    data = request.get_json()
    usuario = data.get("usuario")
    contraseña = data.get("contraseña")
    if not usuario or not contraseña:
        return jsonify({"error": "usuario y contraseña son obligatorios"}), 400
    if user_by_username(usuario):
        return jsonify({"error": "El usuario ya existe"}), 409
    password_hash = bcrypt.generate_password_hash(contraseña).decode("utf-8")
    db = get_db(DB_USERS)
    db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (usuario, password_hash))
    db.commit()
    db.close()
    return jsonify({"message": "Usuario creado", "usuario": usuario}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data.get("usuario")
    contraseña = data.get("contraseña")
    if not usuario or not contraseña:
        return jsonify({"error": "usuario y contraseña son obligatorios"}), 400
    user = user_by_username(usuario)
    if user is None or not bcrypt.check_password_hash(user["password_hash"], contraseña):
        return jsonify({"error": "Credenciales inválidas"}), 401
    return jsonify({"message": f"Login correcto. Bienvenido, {usuario}"}), 200

# ---------- Listar tareas (JSON) ----------
@app.route("/tareas", methods=["GET"])
@require_basic_auth
def listar_tareas(username):
    db = get_db(DB_TASKS)
    cur = db.cursor()
    cur.execute("SELECT id, titulo, descripcion FROM tasks WHERE usuario = ?", (username,))
    tareas = [dict(t) for t in cur.fetchall()]
    db.close()
    return jsonify(tareas), 200


# ---------- Crear tarea ----------
@app.route("/tareas", methods=["POST"])
@require_basic_auth
def crear_tarea(username):
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion", "")

    if not titulo:
        return jsonify({"error": "El título es obligatorio"}), 400

    db = get_db(DB_TASKS)
    db.execute("INSERT INTO tasks (titulo, descripcion, usuario) VALUES (?, ?, ?)",
               (titulo, descripcion, username))
    db.commit()
    db.close()
    return jsonify({"message": "Tarea creada", "titulo": titulo, "usuario": username}), 201

# ---------- Editar tarea ----------
@app.route("/tareas/<int:id>", methods=["PUT"])
@require_basic_auth
def editar_tarea(username, id):
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion")

    db = get_db(DB_TASKS)
    cur = db.cursor()
    # Solo puede editar sus propias tareas
    cur.execute("SELECT * FROM tasks WHERE id = ? AND usuario = ?", (id, username))
    tarea = cur.fetchone()
    if not tarea:
        db.close()
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404

    cur.execute("UPDATE tasks SET titulo = ?, descripcion = ? WHERE id = ?",
                (titulo or tarea["titulo"], descripcion or tarea["descripcion"], id))
    db.commit()
    db.close()
    return jsonify({"message": "Tarea actualizada", "id": id}), 200

# ---------- Eliminar tarea ----------
@app.route("/tareas/<int:id>", methods=["DELETE"])
@require_basic_auth
def eliminar_tarea(username, id):
    db = get_db(DB_TASKS)
    cur = db.cursor()
    # Solo puede eliminar sus propias tareas
    cur.execute("SELECT * FROM tasks WHERE id = ? AND usuario = ?", (id, username))
    tarea = cur.fetchone()
    if not tarea:
        db.close()
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404

    cur.execute("DELETE FROM tasks WHERE id = ?", (id,))
    db.commit()
    db.close()
    return jsonify({"message": "Tarea eliminada", "id": id}), 200


# ------------------- Main -------------------
if __name__ == "__main__":
    if not os.path.exists(DB_USERS):
        init_db()
        print("DB de usuarios creada.")
    if not os.path.exists(DB_TASKS):
        init_tasks_db()
        print("DB de tareas creada.")
    app.run(host="0.0.0.0", port=5000, debug=True)