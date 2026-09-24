from django.db.models import Q

from employees.models import Employee


class EmployeeRepository:
    def get_all(self):
        return Employee.objects.select_related("department")

    def get_for_department(self, department_id):
        # Scope employees in the database, then pass a plain list to the view layer.
        return list(
            Employee.objects.select_related("department")
            .filter(department_id=department_id)
        )

    def filter(self, active=None, department_id=None, search=None, ordering=None):
        queryset = self.get_all()

        if active is not None:
            queryset = queryset.filter(is_active=active)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if search:
            search = search.strip()
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_for_update(self, employee_id):
        return Employee.objects.select_for_update().select_related("department").get(
            pk=employee_id
        )

    def save_department(self, employee, department):
        employee.department = department
        employee.save(update_fields=["department", "updated_at"])
        return employee
