# Employee Management Portal

A web-based Employee Management Portal developed using Python, Flask and REST API architecture.

## Features

- Employee registration with validation
- Employee search by name, email, department or role
- Employee records management with view and delete operations
- SQLite persistence between application restarts
- Responsive browser interface

## Installation and usage

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## REST API

- `GET /api/employees?search=term` - list or search employees
- `POST /api/employees` - register an employee
- `GET /api/employees/<id>` - retrieve one employee
- `PUT /api/employees/<id>` - update an employee
- `DELETE /api/employees/<id>` - remove an employee

Employee JSON fields are `name`, `email`, `department`, `role`, `phone` and `joined_date`.

### Registration workflow

The registration form validates all required employee fields in the browser and sends
the record to `POST /api/employees`. The server validates the payload again and
rejects duplicate email addresses before saving the record.

### Search workflow

The records view calls `GET /api/employees?search=term` as the user types.
Searches match employee names, email addresses, departments and roles.

## Git practical workflow

The project is suitable for the Git and GitHub practical workflow: initialize a repository, create feature branches for employee registration and search, merge them into `development`, resolve documentation conflicts, and push `main` and `development` to the remote repository.