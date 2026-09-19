from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from .models import Employee


@transaction.atomic
def transfer_employee(employee_id, target_department):
    """Move an active employee and lock the row during the update."""
    try:
        employee = Employee.objects.select_for_update().select_related("department").get(
            pk=employee_id
        )
    except Employee.DoesNotExist as exc:
        raise NotFound({"employee": "Employee does not exist."}) from exc

    if not employee.is_active:
        raise ValidationError({"employee": "Inactive employees cannot be transferred."})

    if employee.department_id == target_department.id:
        raise ValidationError({"department_id": "Employee already belongs to this department."})

    employee.department = target_department
    employee.save(update_fields=["department", "updated_at"])
    return employee
