from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from employees.models import Department, Employee
from employees.repositories import EmployeeRepository
from employees.repositories import DepartmentRepository


class EmployeeComponent:
    ALLOWED_ORDERING = {"first_name", "last_name", "hire_date", "created_at"}

    def __init__(self, repository=None):
        self.repository = repository or EmployeeRepository()
        self.department_repository = DepartmentRepository()

    def get_employees_for_department(self, department_id):
        try:
            department = self.department_repository.get_by_id(department_id)
        except Department.DoesNotExist as exc:
            raise NotFound({"department": "Department does not exist."}) from exc

        # Returning a list keeps the controller simple while the repository applies the parent filter.
        return self.repository.get_for_department(department.id)

    def get_employees_list(self, params):
        active = None
        if "active" in params:
            active = self._parse_boolean(params["active"])

        ordering = params.get("ordering")
        if ordering:
            field_name = ordering.removeprefix("-")
            if field_name not in self.ALLOWED_ORDERING:
                choices = ", ".join(sorted(self.ALLOWED_ORDERING))
                raise ValidationError({"ordering": f"Choose one of: {choices}."})

        return self.repository.filter(
            active=active,
            department_id=params.get("department"),
            search=params.get("search"),
            ordering=ordering,
        )

    @transaction.atomic
    def transfer_employee(self, employee_id, target_department):
        try:
            employee = self.repository.get_for_update(employee_id)
        except Employee.DoesNotExist as exc:
            raise NotFound({"employee": "Employee does not exist."}) from exc

        if not employee.is_active:
            raise ValidationError({"employee": "Inactive employees cannot be transferred."})
        if employee.department_id == target_department.id:
            raise ValidationError(
                {"department_id": "Employee already belongs to this department."}
            )

        return self.repository.save_department(employee, target_department)

    @staticmethod
    def _parse_boolean(value):
        values = {"true": True, "1": True, "false": False, "0": False}
        try:
            return values[value.lower()]
        except (AttributeError, KeyError) as exc:
            raise ValidationError({"active": "Use true, false, 1, or 0."}) from exc
