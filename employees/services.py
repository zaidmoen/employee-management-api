"""Backward-compatible service functions.

New business logic belongs in ``employees.components``. This wrapper keeps
existing imports working while callers migrate to the component layer.
"""

from employees.components import EmployeeComponent


def transfer_employee(employee_id, target_department):
    return EmployeeComponent().transfer_employee(employee_id, target_department)
