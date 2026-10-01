from datetime import date

from django.urls import reverse
from rest_framework import status
from sqlalchemy import select

from employees.models.sqlalchemy_models import EmployeeRecord
from employees.sqlalchemy_db import SessionLocal

from .base import ApiTestCase


class EmployeeApiTests(ApiTestCase):
    def employee_payload(self, **changes):
        payload = {
            "first_name": "Maya",
            "last_name": "Saleh",
            "email": "maya@example.com",
            "phone_number": "+970 599 111 222",
            "hire_date": "2025-01-05",
            "is_active": True,
            "department": self.finance.id,
        }
        payload.update(changes)
        return payload

    def test_admin_can_create_employee(self):
        self.authenticate_admin()

        response = self.client.post(reverse("employee-list"), self.employee_payload())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        with SessionLocal() as session:
            exists = session.scalar(
                select(EmployeeRecord.id).where(EmployeeRecord.email == "maya@example.com")
            ) is not None
        self.assertTrue(exists)

    def test_duplicate_email_returns_clear_error(self):
        self.authenticate_admin()

        response = self.client.post(
            reverse("employee-list"),
            self.employee_payload(email="LINA@example.com"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_retrieve_update_and_delete_employee(self):
        self.authenticate_admin()
        detail_url = reverse("employee-detail", args=[self.employee.id])

        retrieve_response = self.client.get(detail_url)
        update_response = self.client.patch(detail_url, {"phone_number": "+970 598 999 999"})
        delete_response = self.client.delete(detail_url)

        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        with SessionLocal() as session:
            exists = session.get(EmployeeRecord, self.employee.id) is not None
        self.assertFalse(exists)

    def test_filter_search_and_ordering(self):
        self.authenticate_regular()
        with SessionLocal.begin() as session:
            session.add(
                EmployeeRecord(
                    first_name="Ahmad",
                    last_name="Zaid",
                    email="ahmad@example.com",
                    hire_date=date(2022, 5, 1),
                    is_active=False,
                    department_id=self.finance.id,
                )
            )

        inactive = self.client.get(reverse("employee-list"), {"active": "false"})
        by_department = self.client.get(
            reverse("employee-list"), {"department": self.engineering.id}
        )
        search = self.client.get(reverse("employee-list"), {"search": "Lina"})
        ordered = self.client.get(reverse("employee-list"), {"ordering": "-hire_date"})

        self.assertEqual(inactive.data["count"], 1)
        self.assertEqual(by_department.data["count"], 1)
        self.assertEqual(search.data["results"][0]["email"], "lina@example.com")
        self.assertEqual(ordered.data["results"][0]["email"], "lina@example.com")

    def test_employee_list_includes_department_name(self):
        self.authenticate_regular()

        response = self.client.get(reverse("employee-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["department_name"], "Engineering")
