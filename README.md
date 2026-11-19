# College Library Management System

## Problem statement

Small college libraries need a straightforward way to record books, issue books to students, and record when books are returned. Managing these details only on paper can make it difficult to check available copies and keep an issue history.

## Objectives

- Store book information and available quantities in an SQLite database.
- Allow a user to add, view, and delete books.
- Issue available books to students and record their names, roll numbers, courses, and issue dates.
- Return issued books, update available quantities, and retain return records.
- Provide a simple web interface that is easy to use in a college practical demonstration.

## Features

- Four working navigation buttons on every page.
- Book management with checks for blank fields and invalid quantities.
- Book issuing only when a copy is available.
- Book returns that update the available quantity exactly once.
- SQLite storage in `library.db`, created automatically beside `app.py`.
- Parameterized database queries and transactions for issuing and returning.

## Languages and technologies used

- **Python 3** for the application logic, validation, database operations, and Flask routes.
- **HTML** for the web pages, forms, navigation buttons, and tables.
- **Jinja** for displaying database records and messages in the HTML templates.
- **SQL** with **SQLite** for creating tables and storing and managing book and issue records.
- **CSS** is limited to a small inline display rule that keeps the navigation forms in one row. No JavaScript is used.
- **Flask** handles web requests and renders the templates; **Waitress** runs the application as a WSGI server.

## Python operations and concepts used

- Variables and basic data types, including strings, integers, and database rows.
- Functions for connecting to the database and initializing its tables.
- Flask route functions, HTTP GET and POST requests, form data, redirects, and URL generation.
- Input validation using string trimming, required-field checks, integer conversion, and conditional statements.
- Exception handling for invalid numbers and SQLite database errors.
- SQLite CRUD operations: `INSERT` to add books and issue records, `SELECT` to display and look up records, `UPDATE` to change book quantities and issue status, and `DELETE` to remove books.
- Parameterized SQL queries to pass values safely to database statements.
- Database transactions to keep issuing and returning operations consistent.
- The `datetime` module to record issue and return dates.
- Jinja template loops and conditions to display table rows and empty-list messages.

## Project files

- `app.py` contains the Flask routes, database setup, input checks, and database operations.
- `templates/` contains the HTML pages displayed by Flask and Jinja.
- `requirements.txt` lists Flask and Waitress, the external packages needed.
- `library.db` is created automatically when the application starts.

## Installation

1. Open the `CollegeLibraryManagementSystem` folder in VS Code.
2. Open the VS Code terminal using **Terminal > New Terminal**.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Activate the environment in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell prevents activation, use Command Prompt and run:

   ```cmd
   .venv\Scripts\activate.bat
   ```

5. Install the required packages:

   ```powershell
   py -m pip install -r requirements.txt
   ```

## Run the application

With the virtual environment active, run the app:

```powershell
py app.py
```

The app uses Waitress, a production WSGI server, instead of Flask's development server. When it starts, the terminal displays the address `http://127.0.0.1:5000`; open that address in a web browser. Stop the application with **Ctrl+C** in the terminal. The book and issue records remain in `library.db` after the application is stopped or restarted.

For a deployment platform that asks for a start command, use this from the project folder:

```text
waitress-serve --host=0.0.0.0 --port=5000 app:app
```
