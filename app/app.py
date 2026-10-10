from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

from config import DB_CONFIG

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def index():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, completed FROM tasks ORDER BY id DESC"
    )

    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")

    if title:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO tasks (title, completed) VALUES (%s, %s)",
            (title, False)
        )

        connection.commit()

        cursor.close()
        connection.close()

    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = NOT completed
        WHERE id = %s
        """,
        (task_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("index"))


@app.route("/health")
def health():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()

        return {"status": "healthy", "database": "connected"}, 200

    except Exception:
        app.logger.exception("Health check failed")
        return {"status": "unhealthy", "database": "unavailable"}, 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)