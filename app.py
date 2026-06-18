from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DATABASE = "database.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        github TEXT,
        image TEXT,
        filename TEXT,
        created_date TEXT
    )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def dashboard():

    conn = get_db()

    projects = conn.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        projects=projects
    )


@app.route("/add", methods=["GET", "POST"])
def add_project():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        github = request.form["github"]

        image_name = ""
        file_name = ""

        image = request.files.get("image")
        project_file = request.files.get("project_file")

        if image and image.filename:

            image_name = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    image_name
                )
            )

        if project_file and project_file.filename:

            file_name = secure_filename(
                project_file.filename
            )

            project_file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    file_name
                )
            )

        conn = get_db()

        conn.execute("""
        INSERT INTO projects(
            title,
            description,
            category,
            github,
            image,
            filename,
            created_date
        )
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            title,
            description,
            category,
            github,
            image_name,
            file_name,
            datetime.now().strftime("%Y-%m-%d")
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_project.html")


@app.route("/project/<int:id>")
def project(id):

    conn = get_db()

    project = conn.execute(
        "SELECT * FROM projects WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "view_project.html",
        project=project
    )


@app.route("/delete/<int:id>")
def delete_project(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM projects WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/uploads/<filename>")
def uploads(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


if __name__ == "__main__":

    init_db()

    app.run(debug=True)