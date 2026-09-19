from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

from employees.models import Employee
from employees.services import transfer_employee
from .base import ApiTestCase


class EmployeeTransferTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.authenticate_admin()

    def transfer_url(self):
        return reverse("employee-transfer", args=[self.employee.id])

    def test_active_employee_can_be_transferred(self):
        response = self.client.post(
            self.transfer_url(), {"department_id": self.finance.id}
        )

        self.employee.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.department, self.finance)

    def test_inactive_employee_transfer_is_rejected_and_rolled_back(self):
        original_department = self.employee.department
        self.employee.is_active = False
        self.employee.save(update_fields=["is_active"])

        response = self.client.post(
            self.transfer_url(), {"department_id": self.finance.id}
        )

        self.employee.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.employee.department, original_department)

    def test_invalid_department_does_not_change_employee(self):
        original_department = self.employee.department

        response = self.client.post(self.transfer_url(), {"department_id": 99999})

        self.employee.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.employee.department, original_department)

    def test_missing_employee_returns_not_found(self):
        response = self.client.post(
            reverse("employee-transfer", args=[99999]),
            {"department_id": self.finance.id},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_database_error_rolls_back_transfer(self):
        original_department = self.employee.department

        with patch.object(Employee, "save", side_effect=RuntimeError("database failure")):
            with self.assertRaises(RuntimeError):
                transfer_employee(self.employee.id, self.finance)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.department, original_department)

