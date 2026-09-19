from django.urls import reverse
from rest_framework import status

from .base import ApiTestCase


class DepartmentApiTests(ApiTestCase):
    def test_department_counts_are_returned(self):
        self.authenticate_regular()

        response = self.client.get(reverse("department-detail", args=[self.engineering.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employee_count"], 1)
        self.assertEqual(response.data["active_employee_count"], 1)

    def test_admin_can_create_update_and_delete_empty_department(self):
        self.authenticate_admin()

        create_response = self.client.post(
            reverse("department-list"), {"name": "Marketing", "description": "Brand team"}
        )
        detail_url = reverse("department-detail", args=[create_response.data["id"]])
        update_response = self.client.patch(detail_url, {"description": "Growth and brand"})
        delete_response = self.client.delete(detail_url)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_department_with_employees_cannot_be_deleted(self):
        self.authenticate_admin()

        response = self.client.delete(
            reverse("department-detail", args=[self.engineering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("department", response.data)

