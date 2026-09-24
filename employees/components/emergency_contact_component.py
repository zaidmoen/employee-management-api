from rest_framework.exceptions import NotFound

from employees.models import Employee
from employees.repositories import EmergencyContactRepository


class EmergencyContactComponent:
    def __init__(self, repository=None):
        self.repository = repository or EmergencyContactRepository()

    def get_contacts_for_employee(self, employee_id):
        employee = self.get_employee(employee_id)
        return self.repository.get_for_employee(employee.id)

    def get_employee(self, employee_id):
        try:
            return self.repository.get_employee(employee_id)
        except Employee.DoesNotExist as exc:
            raise NotFound({"employee": "Employee does not exist."}) from exc
