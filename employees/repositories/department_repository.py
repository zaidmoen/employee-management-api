from django.db.models import Count, Q

from employees.models import Department


class DepartmentRepository:
    def get_all_with_employee_counts(self):
        return Department.objects.annotate(
            employee_count=Count("employees", distinct=True),
            active_employee_count=Count(
                "employees",
                filter=Q(employees__is_active=True),
                distinct=True,
            ),
        )
