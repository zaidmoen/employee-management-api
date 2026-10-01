from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITransactionTestCase
from sqlalchemy import delete

from employees.models.sqlalchemy_models import (
    DepartmentRecord,
    EmergencyContactRecord,
    EmployeeRecord,
    ScheduledShiftRecord,
)
from employees.sqlalchemy_db import SessionLocal


class ApiTestCase(APITransactionTestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin",
            password="admin-pass-123",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username="reader",
            password="reader-pass-123",
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.regular_token = Token.objects.create(user=self.regular_user)

        with SessionLocal.begin() as session:
            self.engineering = DepartmentRecord(name="Engineering")
            self.finance = DepartmentRecord(name="Finance")
            session.add_all([self.engineering, self.finance])
            session.flush()
            self.employee = EmployeeRecord(
                first_name="Lina",
                last_name="Haddad",
                email="lina@example.com",
                phone_number="+970 599 000 001",
                hire_date=date(2024, 1, 15),
                department_id=self.engineering.id,
            )
            session.add(self.employee)
            session.flush()

    def tearDown(self):
        with SessionLocal.begin() as session:
            session.execute(delete(ScheduledShiftRecord))
            session.execute(delete(EmergencyContactRecord))
            session.execute(delete(EmployeeRecord))
            session.execute(delete(DepartmentRecord))
        super().tearDown()

    def authenticate_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

    def authenticate_regular(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.regular_token.key}")
