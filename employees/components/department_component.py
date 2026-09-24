from rest_framework.exceptions import NotFound

from employees.models import Department
from employees.repositories import DepartmentRepository


class DepartmentComponent:
    def __init__(self, repository=None):
        self.repository = repository or DepartmentRepository()

    def get_departments_list(self):
        return self.repository.get_all_with_employee_counts()

    def get_department(self, department_id):
        try:
            return self.repository.get_by_id(department_id)
        except Department.DoesNotExist as exc:
            raise NotFound({"department": "Department does not exist."}) from exc
