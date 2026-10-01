from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from sqlalchemy import select

from employees.repositories import EmployeeRepository
from employees.services import transfer_employee
from employees.models.sqlalchemy_models import EmployeeRecord
from employees.sqlalchemy_db import SessionLocal
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with SessionLocal() as session:
            employee = session.get(EmployeeRecord, self.employee.id)
        self.assertEqual(employee.department_id, self.finance.id)

    def test_inactive_employee_transfer_is_rejected_and_rolled_back(self):
        original_department_id = self.employee.department_id
        with SessionLocal.begin() as session:
            employee = session.get(EmployeeRecord, self.employee.id)
            employee.is_active = False

        response = self.client.post(
            self.transfer_url(), {"department_id": self.finance.id}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with SessionLocal() as session:
            employee = session.get(EmployeeRecord, self.employee.id)
        self.assertEqual(employee.department_id, original_department_id)

    def test_invalid_department_does_not_change_employee(self):
        original_department_id = self.employee.department_id

        response = self.client.post(self.transfer_url(), {"department_id": 99999})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        with SessionLocal() as session:
            employee = session.get(EmployeeRecord, self.employee.id)
        self.assertEqual(employee.department_id, original_department_id)

    def test_missing_employee_returns_not_found(self):
        response = self.client.post(
            reverse("employee-transfer", args=[99999]),
            {"department_id": self.finance.id},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_database_error_rolls_back_transfer(self):
        original_department_id = self.employee.department_id

        with patch.object(EmployeeRepository, "get_by_id", side_effect=RuntimeError("database failure")):
            with self.assertRaises(RuntimeError):
                transfer_employee(self.employee.id, self.finance)

        with SessionLocal() as session:
            employee = session.scalar(
                select(EmployeeRecord).where(EmployeeRecord.id == self.employee.id)
            )
        self.assertEqual(employee.department_id, original_department_id)
