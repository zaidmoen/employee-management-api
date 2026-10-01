from datetime import datetime, timezone

from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from employees.components.validation import load_schema
from employees.components.shift_component import Conflict
from employees.models.sqlalchemy_models import DepartmentRecord
from employees.repositories import DepartmentRepository, EmployeeRepository
from employees.serializers.employee_serializer import EmployeeInputSchema, EmployeePatchSchema
from employees.sqlalchemy_db import SessionLocal


class EmployeeComponent:
    ALLOWED_ORDERING = {"first_name", "last_name", "hire_date", "created_at"}

    def __init__(self, repository=None):
        self.repository = repository or EmployeeRepository()
        self.department_repository = DepartmentRepository()

    def get_employees_for_department(self, department_id):
        with SessionLocal() as session:
            if self.department_repository.get_by_id(session, department_id) is None:
                raise NotFound({"department": "Department does not exist."})
            employees = self.repository.get_for_department(session, department_id)
            return self._detach_all(session, employees)

    def get_employees_list(self, params):
        active = self._parse_boolean(params["active"]) if "active" in params else None
        ordering = params.get("ordering")
        if ordering:
            field_name = ordering.removeprefix("-")
            if field_name not in self.ALLOWED_ORDERING:
                choices = ", ".join(sorted(self.ALLOWED_ORDERING))
                raise ValidationError({"ordering": f"Choose one of: {choices}."})
        department_id = params.get("department") or None
        if department_id is not None:
            try:
                department_id = int(department_id)
            except (TypeError, ValueError) as exc:
                raise ValidationError({"department": "A valid integer is required."}) from exc
        with SessionLocal() as session:
            employees = self.repository.filter(session, active, department_id, params.get("search"), ordering)
            return self._detach_all(session, employees)

    def get_employee(self, employee_id):
        with SessionLocal() as session:
            employee = self.repository.get_by_id(session, employee_id)
            if employee is None:
                raise NotFound({"employee": "Employee does not exist."})
            session.expunge(employee)
            return employee

    def create_employee(self, data, department_override=None):
        if department_override is not None:
            data = data.copy()
            data["department"] = department_override
        values = load_schema(EmployeeInputSchema(), data)
        values["first_name"] = values["first_name"].strip()
        values["last_name"] = values["last_name"].strip()
        values["email"] = values["email"].strip().lower()
        values["phone_number"] = values["phone_number"].strip()
        department_id = department_override or values.pop("department")
        if department_override:
            values.pop("department", None)
        with SessionLocal() as session:
            with session.begin():
                if self.department_repository.get_by_id(session, department_id) is None:
                    raise ValidationError({"department": "The selected department does not exist."})
                if self.repository.get_email_match(session, values["email"]):
                    raise ValidationError({"email": "An employee with this email already exists."})
                values["department_id"] = department_id
                employee = self.repository.create(session, values)
                employee.department_name = session.scalar(select(DepartmentRecord.name).where(DepartmentRecord.id == department_id))
            session.expunge(employee)
            return employee

    def update_employee(self, employee_id, data, partial=True):
        values = load_schema(EmployeePatchSchema(), data)
        if not partial:
            required = {"first_name", "last_name", "email", "hire_date", "department"}
            missing = {field: ["Missing data for required field."] for field in required if field not in values}
            if missing:
                raise ValidationError(missing)
        with SessionLocal() as session:
            try:
                with session.begin():
                    employee = self.repository.get_by_id(session, employee_id, lock=True)
                    if employee is None:
                        raise NotFound({"employee": "Employee does not exist."})
                    values = self._normalize_employee_values(values)
                    if "department" in values:
                        department_id = values.pop("department")
                        if self.department_repository.get_by_id(session, department_id) is None:
                            raise ValidationError({"department": "The selected department does not exist."})
                        values["department_id"] = department_id
                    if "email" in values and self.repository.get_email_match(session, values["email"], employee_id):
                        raise ValidationError({"email": "An employee with this email already exists."})
                    for field, value in values.items():
                        setattr(employee, field, value)
                    employee.updated_at = datetime.now(timezone.utc)
                    employee.department_name = session.scalar(select(DepartmentRecord.name).where(DepartmentRecord.id == employee.department_id))
            except IntegrityError as exc:
                raise ValidationError({"detail": "Employee data conflicts with an existing record."}) from exc
            session.expunge(employee)
            return employee

    def delete_employee(self, employee_id):
        with SessionLocal() as session:
            with session.begin():
                employee = self.repository.get_by_id(session, employee_id, lock=True)
                if employee is None:
                    raise NotFound({"employee": "Employee does not exist."})
                if self.repository.has_shifts(session, employee_id):
                    raise Conflict({"detail": "Employee has scheduled shifts and cannot be deleted."})
                session.delete(employee)

    def transfer_employee(self, employee_id, target_department):
        department_id = getattr(target_department, "id", target_department)
        with SessionLocal() as session:
            with session.begin():
                employee = self.repository.get_by_id(session, employee_id, lock=True)
                if employee is None:
                    raise NotFound({"employee": "Employee does not exist."})
                department = self.department_repository.get_by_id(session, department_id)
                if department is None:
                    raise ValidationError({"department_id": "The target department does not exist."})
                if not employee.is_active:
                    raise ValidationError({"employee": "Inactive employees cannot be transferred."})
                if employee.department_id == department.id:
                    raise ValidationError({"department_id": "Employee already belongs to this department."})
                employee.department_id = department.id
                employee.department_name = department.name
                employee.updated_at = datetime.now(timezone.utc)
            session.expunge(employee)
            return employee

    @staticmethod
    def _normalize_employee_values(values):
        for name in ("first_name", "last_name"):
            if name in values:
                values[name] = values[name].strip()
                if not values[name]:
                    raise ValidationError({name: "This field cannot be blank."})
        if "email" in values:
            values["email"] = values["email"].strip().lower()
        if "phone_number" in values:
            values["phone_number"] = values["phone_number"].strip()
        return values

    @staticmethod
    def _detach_all(session, records):
        for record in records:
            session.expunge(record)
        return records

    @staticmethod
    def _parse_boolean(value):
        values = {"true": True, "1": True, "false": False, "0": False}
        try:
            return values[value.lower()]
        except (AttributeError, KeyError) as exc:
            raise ValidationError({"active": "Use true, false, 1, or 0."}) from exc
