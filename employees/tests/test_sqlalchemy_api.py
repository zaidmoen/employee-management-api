from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from sqlalchemy import select

from employees.database import Base, SessionLocal, engine
from employees.sqlalchemy_models import Department, Employee, EmergencyContact


class SqlAlchemyApiTests(APITestCase):
    def setUp(self):
        Base.metadata.create_all(engine)
        self.admin = get_user_model().objects.create_user(username="admin", password="pass", is_staff=True)
        self.reader = get_user_model().objects.create_user(username="reader", password="pass")
        self.admin_token = Token.objects.create(user=self.admin)
        self.reader_token = Token.objects.create(user=self.reader)
        with SessionLocal.begin() as session:
            department = Department(name="Engineering", description="")
            session.add(department)
            session.flush()
            self.department_id = department.id
            employee = Employee(first_name="Lina", last_name="Haddad", email="lina@example.com",
                                hire_date=date(2024, 1, 15), department=department)
            session.add(employee)
            session.flush()
            self.employee_id = employee.id

    def tearDown(self):
        Base.metadata.drop_all(engine)

    def auth(self, admin=True):
        token = self.admin_token if admin else self.reader_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_permissions_and_department_counts(self):
        url = reverse("department-list")
        self.assertEqual(self.client.get(url).status_code, 401)
        self.auth(False)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["employee_count"], 1)
        self.assertEqual(self.client.post(url, {"name": "Finance"}).status_code, 403)

    def test_employee_nested_routes_and_parent_scoping(self):
        self.auth()
        url = reverse("department-employees-list", args=[self.department_id])
        self.assertEqual(self.client.get(url).data["count"], 1)
        created = self.client.post(url, {"first_name": "Maya", "last_name": "Saleh",
                                         "email": "maya@example.com", "hire_date": "2025-01-05"})
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["department"], self.department_id)
        other = self.client.post(reverse("department-list"), {"name": "Finance"}).data["id"]
        wrong = reverse("department-employees-detail", args=[other, self.employee_id])
        self.assertEqual(self.client.get(wrong).status_code, 404)

    def test_shift_calculation_and_validation(self):
        self.auth()
        url = reverse("employee-detail", args=[self.employee_id])
        result = self.client.patch(url, {"shift_start": "22:00", "shift_end": "06:00", "break_minutes": 30})
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(result.data["shift_hours"], 7.5)
        invalid = self.client.patch(url, {"break_minutes": 500})
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(self.client.get(url).data["break_minutes"], 30)

    def test_duplicate_email_and_filter(self):
        self.auth()
        url = reverse("employee-list")
        duplicate = self.client.post(url, {"first_name": "Maya", "last_name": "Saleh",
                                            "email": "LINA@example.com", "hire_date": "2025-01-05",
                                            "department": self.department_id})
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn("email", duplicate.data)
        self.assertEqual(self.client.get(url, {"search": "lin"}).data["count"], 1)
        self.assertEqual(self.client.get(url, {"active": "wrong"}).status_code, 400)

    def test_contact_parent_and_crud(self):
        self.auth()
        url = reverse("employee-contacts-list", args=[self.employee_id])
        contact = self.client.post(url, {"name": "John", "relationship": "Parent",
                                         "phone_number": "+970 599 123 456", "email": "john@example.com"})
        self.assertEqual(contact.status_code, 201, contact.data)
        detail = reverse("employee-contacts-detail", args=[self.employee_id, contact.data["id"]])
        self.assertEqual(self.client.patch(detail, {"relationship": "Father"}).data["relationship"], "Father")
        self.assertEqual(self.client.delete(detail).status_code, 204)
        self.assertEqual(self.client.get(detail).status_code, 404)

    def test_transfer_and_inactive_rule(self):
        self.auth()
        finance = self.client.post(reverse("department-list"), {"name": "Finance"}).data["id"]
        url = reverse("employee-transfer", args=[self.employee_id])
        self.assertEqual(self.client.post(url, {"department_id": finance}).status_code, 200)
        self.assertEqual(self.client.post(url, {"department_id": finance}).status_code, 400)
        self.client.patch(reverse("employee-detail", args=[self.employee_id]), {"is_active": False})
        self.assertEqual(self.client.post(url, {"department_id": self.department_id}).status_code, 400)

    def test_delete_department_with_employees_is_rejected(self):
        self.auth()
        self.assertEqual(self.client.delete(reverse("department-detail", args=[self.department_id])).status_code, 400)

    def test_department_update_and_delete_after_employee_transfer(self):
        self.auth()
        finance = self.client.post(reverse("department-list"), {"name": "Finance"}).data["id"]
        detail = reverse("department-detail", args=[finance])
        self.assertEqual(self.client.patch(detail, {"description": "Accounting"}).data["description"], "Accounting")
        self.assertEqual(self.client.delete(detail).status_code, 204)
        self.assertEqual(self.client.get(detail).status_code, 404)

    def test_wrong_contact_parent_is_not_exposed(self):
        self.auth()
        other = self.client.post(reverse("department-list"), {"name": "Finance"}).data["id"]
        employee = self.client.post(reverse("employee-list"), {"first_name": "Maya", "last_name": "Saleh",
            "email": "maya@example.com", "hire_date": "2025-01-01", "department": other}).data["id"]
        contact = self.client.post(reverse("employee-contacts-list", args=[employee]), {
            "name": "John", "relationship": "Father", "phone_number": "+970 599 123 456", "email": "john@example.com"}).data["id"]
        wrong = reverse("employee-contacts-detail", args=[self.employee_id, contact])
        self.assertEqual(self.client.get(wrong).status_code, 404)
        self.assertEqual(self.client.patch(wrong, {"name": "Wrong"}).status_code, 404)

    def test_employee_delete_cascades_contacts(self):
        self.auth()
        contact = self.client.post(reverse("employee-contacts-list", args=[self.employee_id]), {
            "name": "John", "relationship": "Father", "phone_number": "+970 599 123 456", "email": "john@example.com"})
        self.assertEqual(contact.status_code, 201)
        self.assertEqual(self.client.delete(reverse("employee-detail", args=[self.employee_id])).status_code, 204)
        with SessionLocal() as session:
            self.assertEqual(list(session.scalars(select(EmergencyContact))), [])
