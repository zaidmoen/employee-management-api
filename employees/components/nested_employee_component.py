from rest_framework.exceptions import NotFound, ValidationError

from employees.repositories import NestedDepartmentRepository, NestedEmployeeRepository


class NestedEmployeeComponent:
    def __init__(self, employee_repository=None, department_repository=None):
        self.employee_repository = employee_repository or NestedEmployeeRepository()
        self.department_repository = department_repository or NestedDepartmentRepository()

    def get_department(self, department_id):
        department = self.department_repository.get_by_id(department_id)
        if department is None:
            raise NotFound({"department": "Department does not exist."})
        return department

    def get_employees_for_department(self, department_id):
        department = self.get_department(department_id)
        # The repository scopes the rows before returning a regular Python list.
        return self.employee_repository.get_for_department(department.id)

    def create_employee(self, department, employee_data):
        if self.employee_repository.email_exists(employee_data["email"]):
            raise ValidationError(
                {"email": "An employee with this email already exists."}
            )
        return self.employee_repository.create_for_department(department, employee_data)
