from django.urls import reverse
from rest_framework import status

from .base import ApiTestCase


class PermissionTests(ApiTestCase):
    def test_unauthenticated_user_cannot_read_or_write(self):
        list_response = self.client.get(reverse("employee-list"))
        create_response = self.client.post(reverse("department-list"), {"name": "Sales"})

        self.assertIn(list_response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        self.assertIn(create_response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_regular_user_can_read_but_cannot_write(self):
        self.authenticate_regular()

        list_response = self.client.get(reverse("employee-list"))
        create_response = self.client.post(reverse("department-list"), {"name": "Sales"})

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_write(self):
        self.authenticate_admin()

        response = self.client.post(reverse("department-list"), {"name": "Sales"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

