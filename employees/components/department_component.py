from datetime import datetime, timezone

from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.models.sqlalchemy_models import DepartmentRecord
from employees.repositories import DepartmentRepository
from employees.serializers.department_serializer import DepartmentInputSchema
from employees.sqlalchemy_db import SessionLocal
from employees.components.validation import load_schema


class DepartmentComponent:
    def __init__(self, repository=None):
        self.repository = repository or DepartmentRepository()

    def get_departments_list(self):
        with SessionLocal() as session:
            return self.repository.get_all_with_employee_counts(session)

    def get_department(self, department_id):
        with SessionLocal() as session:
            department = self.repository.get_by_id(session, department_id)
            if department is None:
                raise NotFound({"department": "Department does not exist."})
            return department

    def create_department(self, data):
        values = load_schema(DepartmentInputSchema(), data)
        values["name"] = values["name"].strip()
        with SessionLocal() as session:
            try:
                with session.begin():
                    department = self.repository.create(session, values)
                    department.employee_count = 0
                    department.active_employee_count = 0
            except IntegrityError as exc:
                raise ValidationError({"name": "Department with this name already exists."}) from exc
            session.expunge(department)
            return department

    def update_department(self, department_id, data, partial=True):
        values = load_schema(DepartmentInputSchema(partial=partial), data)
        if "name" in values:
            values["name"] = values["name"].strip()
        with SessionLocal() as session:
            try:
                with session.begin():
                    department = self.repository.get_by_id(session, department_id)
                    if department is None:
                        raise NotFound({"department": "Department does not exist."})
                    for field, value in values.items():
                        setattr(department, field, value)
                    department.updated_at = datetime.now(timezone.utc)
            except IntegrityError as exc:
                raise ValidationError({"name": "Department with this name already exists."}) from exc
            session.expunge(department)
            return department

    def delete_department(self, department_id):
        with SessionLocal() as session:
            with session.begin():
                department = self.repository.get_by_id(session, department_id)
                if department is None:
                    raise NotFound({"department": "Department does not exist."})
                if self.repository.has_employees(session, department_id):
                    raise ValidationError({"department": "Move or delete this department's employees first."})
                session.delete(department)
