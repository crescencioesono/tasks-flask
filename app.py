from flask import Flask, render_template, request, redirect
from sqlite3 import connect

app = Flask(__name__, static_folder="static")

def init_db():
    with connect("db.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )""")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                FOREIGN KEY (user_id) REFERENCES users(id)
            )""")
        conn.commit()

init_db()

def connect_db():
    return connect("db.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register-page", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_user():
    try:
        username = request.form.get("username")
        password = request.form.get("password")

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, password))
        conn.commit()
        conn.close()
        return redirect("/")
    except Exception as e:
        return {"Error": str(e)}

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    global user_id

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password))
    user = cursor.fetchone()
    user_id = user[0]
    conn.close()

    if user:
        return redirect("/dashboard")
    else:
        return {"Error": "Usuario no encontrado"}, 404
    
@app.route("/dashboard", methods=["GET"])
def dashboard():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", tasks=tasks)

@app.route("/register-task", methods=["POST"])
def register_task():
    name = request.form.get("name")
    description = request.form.get("description")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, name, description) VALUES (?, ?, ?)", (user_id, name, description))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/delete-task/<id>", methods=["GET"])
def delete_task(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)