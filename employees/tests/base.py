from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from employees.models import Department, Employee


class ApiTestCase(APITestCase):
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

        self.engineering = Department.objects.create(name="Engineering")
        self.finance = Department.objects.create(name="Finance")
        self.employee = Employee.objects.create(
            first_name="Lina",
            last_name="Haddad",
            email="lina@example.com",
            phone_number="+970 599 000 001",
            hire_date=date(2024, 1, 15),
            department=self.engineering,
        )

    def authenticate_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

    def authenticate_regular(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.regular_token.key}")

