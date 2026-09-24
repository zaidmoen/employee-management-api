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
        employee = self.repository.get_employee(employee_id)
        if employee is None:
            raise NotFound({"employee": "Employee does not exist."})
        return employee

    def create_contact(self, employee, contact_data):
        return self.repository.create_for_employee(employee, contact_data)

    def update_contact(self, employee_id, contact, changes):
        updated_contact = self.repository.update_for_employee(
            employee_id,
            contact,
            changes,
        )
        if updated_contact is None:
            raise NotFound("The requested contact does not exist under this employee.")
        return updated_contact

    def delete_contact(self, employee_id, contact_id):
        deleted = self.repository.delete_for_employee(employee_id, contact_id)
        if not deleted:
            raise NotFound("The requested contact does not exist under this employee.")
