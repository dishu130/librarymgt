import os
import sqlite3
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from waitress import serve


app = Flask(__name__)
app.secret_key = "college-library-management-system"

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")


def connect_to_database():
    """Open the SQLite database and enable foreign-key checks."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create the required tables the first time the application runs."""
    connection = connect_to_database()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                author TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS issued_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                roll_number TEXT NOT NULL,
                student_course TEXT NOT NULL DEFAULT '',
                issue_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL DEFAULT 'Issued',
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
            """
        )
        issue_columns = connection.execute(
            "PRAGMA table_info(issued_books)"
        ).fetchall()
        if not any(column["name"] == "student_course" for column in issue_columns):
            connection.execute(
                "ALTER TABLE issued_books ADD COLUMN student_course TEXT NOT NULL DEFAULT ''"
            )
        connection.commit()
    finally:
        connection.close()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/books", methods=["GET", "POST"])
def manage_books():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        author = request.form.get("author", "").strip()
        quantity_text = request.form.get("quantity", "").strip()

        if not name or not author or not quantity_text:
            flash("Please enter the book name, author name, and quantity.", "error")
        else:
            try:
                quantity = int(quantity_text)
                if quantity < 0:
                    flash("Quantity cannot be negative.", "error")
                else:
                    connection = connect_to_database()
                    try:
                        connection.execute(
                            "INSERT INTO books (name, author, quantity) VALUES (?, ?, ?)",
                            (name, author, quantity),
                        )
                        connection.commit()
                        flash("Book added successfully.", "success")
                    except sqlite3.Error as error:
                        connection.rollback()
                        print("Could not add book:", error)
                        flash("The book could not be saved because of a database error.", "error")
                    finally:
                        connection.close()
            except ValueError:
                flash("Please enter a whole number for quantity.", "error")

        return redirect(url_for("manage_books"))

    connection = connect_to_database()
    try:
        books = connection.execute(
            "SELECT id, name, author, quantity FROM books ORDER BY id"
        ).fetchall()
    finally:
        connection.close()
    return render_template("books.html", books=books)


@app.route("/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    connection = connect_to_database()
    try:
        cursor = connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        connection.commit()
        if cursor.rowcount == 0:
            flash("That book was not found.", "error")
        else:
            flash("Book deleted successfully.", "success")
    except sqlite3.IntegrityError:
        connection.rollback()
        flash("This book has issue records and cannot be deleted.", "error")
    except sqlite3.Error as error:
        connection.rollback()
        print("Could not delete book:", error)
        flash("The book could not be deleted because of a database error.", "error")
    finally:
        connection.close()
    return redirect(url_for("manage_books"))


@app.route("/issue", methods=["GET", "POST"])
def issue_book():
    if request.method == "POST":
        book_id_text = request.form.get("book_id", "").strip()
        student_name = request.form.get("student_name", "").strip()
        roll_number = request.form.get("roll_number", "").strip()
        student_course = request.form.get("student_course", "").strip()

        if not book_id_text or not student_name or not roll_number or not student_course:
            flash(
                "Please select a book and enter the student name, roll number, and course.",
                "error",
            )
            return redirect(url_for("issue_book"))

        try:
            book_id = int(book_id_text)
        except ValueError:
            flash("Please select a valid book.", "error")
            return redirect(url_for("issue_book"))

        connection = connect_to_database()
        try:
            connection.execute("BEGIN IMMEDIATE")
            book = connection.execute(
                "SELECT quantity FROM books WHERE id = ?", (book_id,)
            ).fetchone()
            if book is None:
                connection.rollback()
                flash("The selected book was not found.", "error")
            elif book["quantity"] <= 0:
                connection.rollback()
                flash("This book is not currently available.", "error")
            else:
                connection.execute(
                    "UPDATE books SET quantity = quantity - 1 WHERE id = ?",
                    (book_id,),
                )
                connection.execute(
                    """
                    INSERT INTO issued_books
                        (book_id, student_name, roll_number, student_course, issue_date, status)
                    VALUES (?, ?, ?, ?, ?, 'Issued')
                    """,
                    (
                        book_id,
                        student_name,
                        roll_number,
                        student_course,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ),
                )
                connection.commit()
                flash("Book issued successfully.", "success")
        except sqlite3.Error as error:
            connection.rollback()
            print("Could not issue book:", error)
            flash("The book could not be issued because of a database error.", "error")
        finally:
            connection.close()
        return redirect(url_for("issue_book"))

    connection = connect_to_database()
    try:
        books = connection.execute(
            "SELECT id, name, author, quantity FROM books WHERE quantity > 0 ORDER BY name"
        ).fetchall()
    finally:
        connection.close()
    return render_template("issue.html", books=books)


@app.route("/issued-books")
def view_issued_books():
    connection = connect_to_database()
    try:
        issued_books = connection.execute(
            """
            SELECT issued_books.id, books.name AS book_name,
                   issued_books.student_name, issued_books.roll_number,
                   issued_books.student_course,
                   issued_books.issue_date
            FROM issued_books
            JOIN books ON issued_books.book_id = books.id
            WHERE issued_books.status = 'Issued'
            ORDER BY issued_books.id
            """
        ).fetchall()
    finally:
        connection.close()
    return render_template("issued_books.html", issued_books=issued_books)


@app.route("/return/<int:issue_id>", methods=["POST"])
def return_book(issue_id):
    connection = connect_to_database()
    try:
        connection.execute("BEGIN IMMEDIATE")
        issue = connection.execute(
            "SELECT book_id FROM issued_books WHERE id = ? AND status = 'Issued'",
            (issue_id,),
        ).fetchone()
        if issue is None:
            connection.rollback()
            flash("This book has already been returned or the issue record was not found.", "error")
        else:
            connection.execute(
                """
                UPDATE issued_books
                SET status = 'Returned', return_date = ?
                WHERE id = ? AND status = 'Issued'
                """,
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), issue_id),
            )
            connection.execute(
                "UPDATE books SET quantity = quantity + 1 WHERE id = ?",
                (issue["book_id"],),
            )
            connection.commit()
            flash("Book returned successfully.", "success")
    except sqlite3.Error as error:
        connection.rollback()
        print("Could not return book:", error)
        flash("The book could not be returned because of a database error.", "error")
    finally:
        connection.close()
    return redirect(url_for("view_issued_books"))


initialize_database()


if __name__ == "__main__":
    print("College Library Management System is available at http://127.0.0.1:5000", flush=True)
    serve(app, host="0.0.0.0", port=5000)
