from django.urls import reverse
from rest_framework import status

from employees.models import EmergencyContact, Employee
from employees.repositories import EmergencyContactRepository, NestedEmployeeRepository

from .base import ApiTestCase


class DepartmentEmployeeApiTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.finance_employee = Employee.objects.create(
            first_name="Maya",
            last_name="Saleh",
            email="maya@example.com",
            hire_date="2025-01-05",
            department=self.finance,
        )

    def test_list_only_returns_employees_in_the_department(self):
        self.authenticate_regular()

        response = self.client.get(
            reverse("department-employees-list", args=[self.engineering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.employee.id)

    def test_employee_can_be_retrieved_through_its_department(self):
        self.authenticate_regular()

        response = self.client.get(
            reverse(
                "department-employees-detail",
                args=[self.engineering.id, self.employee.id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "lina@example.com")

    def test_admin_can_create_employee_under_department_in_url(self):
        self.authenticate_admin()

        response = self.client.post(
            reverse("department-employees-list", args=[self.engineering.id]),
            {
                "first_name": "Rana",
                "last_name": "Khalil",
                "email": "rana@example.com",
                "hire_date": "2025-02-01",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["department"], self.engineering.id)
        self.assertTrue(NestedEmployeeRepository().email_exists("rana@example.com"))

    def test_employee_from_another_department_returns_404(self):
        self.authenticate_regular()

        response = self.client.get(
            reverse(
                "department-employees-detail",
                args=[self.engineering.id, self.finance_employee.id],
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_department_returns_404(self):
        self.authenticate_regular()

        response = self.client.get(reverse("department-employees-list", args=[99999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_department_cannot_be_used_for_employee_creation(self):
        self.authenticate_admin()

        response = self.client.post(
            reverse("department-employees-list", args=[99999]),
            {
                "first_name": "Rana",
                "last_name": "Khalil",
                "email": "rana@example.com",
                "hire_date": "2025-02-01",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class EmergencyContactApiTests(ApiTestCase):
    def contact_payload(self, **changes):
        payload = {
            "name": "John Doe",
            "relationship": "Father",
            "phone_number": "+123 456 7890",
            "email": "john@example.com",
        }
        payload.update(changes)
        return payload

    def contacts_url(self, employee_id=None):
        employee_id = employee_id or self.employee.id
        return reverse("employee-contacts-list", args=[employee_id])

    def contact_url(self, contact_id, employee_id=None):
        employee_id = employee_id or self.employee.id
        return reverse("employee-contacts-detail", args=[employee_id, contact_id])

    def test_admin_can_create_and_list_employee_contacts(self):
        self.authenticate_admin()

        create_response = self.client.post(
            self.contacts_url(), self.contact_payload()
        )
        list_response = self.client.get(self.contacts_url())

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["email"], "john@example.com")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(list_response.data["results"][0]["id"], create_response.data["id"])

    def test_contact_can_be_retrieved_updated_and_deleted(self):
        self.authenticate_admin()
        contact = EmergencyContact.objects.create(
            employee=self.employee,
            **self.contact_payload(),
        )

        detail_url = self.contact_url(contact.id)
        retrieve_response = self.client.get(detail_url)
        update_response = self.client.patch(detail_url, {"relationship": "Parent"})
        delete_response = self.client.delete(detail_url)

        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["relationship"], "Father")
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["relationship"], "Parent")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            EmergencyContactRepository().get_for_employee(self.employee.id),
            [],
        )

    def test_contact_owned_by_another_employee_returns_404(self):
        self.authenticate_regular()
        other_employee = Employee.objects.create(
            first_name="Maya",
            last_name="Saleh",
            email="maya@example.com",
            hire_date="2025-01-05",
            department=self.finance,
        )
        contact = EmergencyContact.objects.create(
            employee=other_employee,
            **self.contact_payload(),
        )

        response = self.client.get(self.contact_url(contact.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_employee_returns_404_for_list_and_create(self):
        self.authenticate_admin()
        contacts_url = self.contacts_url(99999)

        list_response = self.client.get(contacts_url)
        create_response = self.client.post(contacts_url, self.contact_payload())

        self.assertEqual(list_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(create_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_contact_validation_returns_field_errors(self):
        self.authenticate_admin()

        response = self.client.post(
            self.contacts_url(),
            self.contact_payload(phone_number="bad", email="not-an-email"),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)
        self.assertIn("email", response.data)

    def test_regular_user_can_read_but_cannot_write_contacts(self):
        self.authenticate_regular()

        list_response = self.client.get(self.contacts_url())
        create_response = self.client.post(
            self.contacts_url(), self.contact_payload()
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_read_contacts(self):
        response = self.client.get(self.contacts_url())

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )
