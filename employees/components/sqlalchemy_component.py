"""Business checks sit between the HTTP controller and repository."""
from rest_framework.exceptions import NotFound, ValidationError

from employees.sqlalchemy_models import Department, Employee, EmergencyContact
from employees.repositories.sqlalchemy_repository import Repository


class EmployeeComponent:
    ORDERING = {"first_name", "last_name", "hire_date", "created_at"}

    def __init__(self, session):
        self.repo = Repository(session)

    def require(self, model, item_id, **kwargs):
        item = self.repo.get(model, item_id, **kwargs)
        if item is None:
            raise NotFound({model.__name__.lower(): "Not found."})
        return item

    def list_employees(self, params, department_id=None):
        active = params.get("active")
        if active is not None:
            values = {"true": True, "1": True, "false": False, "0": False}
            if active.lower() not in values:
                raise ValidationError({"active": "Use true, false, 1, or 0."})
            active = values[active.lower()]
        ordering = params.get("ordering")
        if ordering and ordering.lstrip("-") not in self.ORDERING:
            raise ValidationError({"ordering": "Unsupported ordering field."})
        selected_department = department_id or params.get("department")
        if selected_department is not None:
            try:
                selected_department = int(selected_department)
            except (TypeError, ValueError):
                raise ValidationError({"department": "Use an integer department id."})
        return self.repo.list_employees(active, selected_department, params.get("search"), ordering)

    def check_shift(self, values):
        start, end = values.get("shift_start"), values.get("shift_end")
        if (start is None) != (end is None):
            raise ValidationError({"shift_start": "Set both shift_start and shift_end."})
        if start is not None:
            minutes = ((end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)) % 1440 or 1440
            if values.get("break_minutes", 0) >= minutes:
                raise ValidationError({"break_minutes": "Break must be shorter than the shift."})
        elif values.get("break_minutes", 0):
            raise ValidationError({"break_minutes": "Set shift times before adding a break."})

    def save_employee(self, data, employee=None):
        department_id = data.pop("department", employee.department_id if employee else None)
        department = self.repo.get(Department, department_id)
        if department is None:
            raise ValidationError({"department": "The selected department does not exist."})
        if self.repo.email_exists(data.get("email", employee.email if employee else ""), employee.id if employee else None):
            raise ValidationError({"email": "An employee with this email already exists."})
        combined = {"shift_start": employee.shift_start if employee else None,
                    "shift_end": employee.shift_end if employee else None,
                    "break_minutes": employee.break_minutes if employee else 0}
        combined.update(data)
        self.check_shift(combined)
        employee = employee or Employee()
        for field, value in data.items():
            setattr(employee, field, value)
        employee.department = department
        return self.repo.add(employee)

    def transfer(self, employee_id, department_id):
        employee = self.require(Employee, employee_id, lock=True)
        department = self.repo.get(Department, department_id)
        if department is None:
            raise ValidationError({"department_id": "The target department does not exist."})
        if not employee.is_active:
            raise ValidationError({"employee": "Inactive employees cannot be transferred."})
        if employee.department_id == department.id:
            raise ValidationError({"department_id": "Employee already belongs to this department."})
        employee.department = department
        self.repo.session.flush()
        return employee
