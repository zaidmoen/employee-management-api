from employees.models import Employee, EmergencyContact


class EmergencyContactRepository:
    def get_employee(self, employee_id):
        return Employee.objects.get(pk=employee_id)

    def get_for_employee(self, employee_id):
        return list(
            EmergencyContact.objects.select_related("employee")
            .filter(employee_id=employee_id)
        )

    def create_for_employee(self, employee, contact_data):
        return EmergencyContact.objects.create(employee=employee, **contact_data)
