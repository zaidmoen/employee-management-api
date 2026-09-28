# Employee Management API

A training REST API built with Django REST Framework, SQLAlchemy 2.0, marshmallow-sqlalchemy, MySQL, and `drf-nested-routers`.

Django handles token authentication, permissions, URLs, and historical schema migrations. Employee, department, and contact reads/writes use SQLAlchemy sessions. Marshmallow validates input and serializes the SQLAlchemy objects. The flow is **controller → component → repository → SQLAlchemy**, with a commit on success and rollback on errors.

## Setup

Use Python 3.11+ and MySQL 8. Create `employee_management_db` with `database/create_database.sql` (MySQL Workbench also works). Then:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` in the project root:

```dotenv
MYSQL_DATABASE=employee_management_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
DJANGO_SECRET_KEY=replace_for_real_deployments
DJANGO_DEBUG=True
```

Run the **new migration before starting the API**. Migration 0005 adds optional shift fields; 0006 removes Django's live model state while retaining all existing employee tables and rows for SQLAlchemy.

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

Django admin manages users and tokens; employee data is managed through the API. Existing user tokens continue to work. Obtain a token with `POST http://127.0.0.1:8000/api/token/` and send `Authorization: Token YOUR_TOKEN` in API requests. Authenticated users can read; staff can write. Every URL ends in `/`.

## URLs

| Method | URL | Use |
| --- | --- | --- |
| GET, POST | `/api/departments/` | List with employee totals, create |
| GET, PUT, PATCH, DELETE | `/api/departments/{id}/` | Department detail and changes |
| GET, POST | `/api/employees/` | Filter/list and create |
| GET, PUT, PATCH, DELETE | `/api/employees/{id}/` | Employee detail and changes |
| POST | `/api/employees/{id}/transfer/` | Change department of an active employee |
| GET, POST | `/api/departments/{dep_id}/employees/` | Employees in department, create under parent |
| GET | `/api/departments/{dep_id}/employees/{emp_id}/` | Parent-scoped employee |
| GET, POST | `/api/employees/{emp_id}/contacts/` | Contact list and create |
| GET, PUT, PATCH, DELETE | `/api/employees/{emp_id}/contacts/{contact_id}/` | Parent-scoped contact |

Employee list supports `?active=true`, `?department=1`, `?search=lina`, and `?ordering=-hire_date`. Ordering accepts first_name, last_name, hire_date, and created_at. Lists are paginated. `joinedload` loads the department for an employee list/detail so serialization does not make a department query per employee.

### Shift example

Set `shift_start`, `shift_end`, and `break_minutes` on employee create or PATCH:

```http
PATCH /api/employees/1/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{"shift_start":"22:00","shift_end":"06:00","break_minutes":30}
```

The response includes `shift_hours: 7.5`. Times are local wall-clock times; an end before a start means the shift crosses midnight, and equal start/end means 24 hours. A break must be shorter than the shift. These are **scheduled hours per shift**, not payroll calculations; there are no timezone, date, holiday, or overtime rules yet. Employees without a shift return `shift_hours: null`.

### Nested employee example

```http
POST /api/departments/1/employees/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{"first_name":"Rana","last_name":"Khalil","email":"rana@example.com","hire_date":"2025-02-01"}
```

The department comes from the URL; a child belonging to another parent returns 404. Transfer uses `{"department_id": 2}`. Invalid input returns field errors and the SQLAlchemy session rolls back.

## Code map

- `employees/sqlalchemy_models.py`: typed mappings and relationships.
- `employees/database.py`: engine and one session per operation.
- `employees/serializers/schemas.py`: marshmallow input and SQLAlchemy output schemas.
- `employees/repositories/sqlalchemy_repository.py`: database statements returning Python lists.
- `employees/components/sqlalchemy_component.py`: shift, transfer, and uniqueness rules.
- `employees/views/sqlalchemy_controller.py`: small DRF ViewSet actions and responses.
- `employees/urls.py`: root and nested routers.
- `employees/migrations/`: historical Django schema and data migrations, plus handover to SQLAlchemy.

To debug an API, put a breakpoint in `EmployeeViewSet.create()` in `employees/views/sqlalchemy_controller.py`, then step into `EmployeeComponent.save_employee()`, `Repository.add()`, and `session_scope()`. Example: `python -m pdb manage.py runserver --noreload`, send `POST /api/employees/` from Postman, inspect `data`, `department`, and `session.new`, then continue. The debugger stops at startup first; use `b employees/views/sqlalchemy_controller.py:110` adjusted to the current line, then `c`. In an IDE, set the breakpoint directly in the controller instead.

## Checks

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --settings=employee_api.test_settings
```

The tests use SQLite and check auth, nested routes, validation, scheduled shift hours, rollback, contacts, and transfer. MySQL schema compatibility still requires running `migrate` on a local MySQL database. Never commit `.env`.
