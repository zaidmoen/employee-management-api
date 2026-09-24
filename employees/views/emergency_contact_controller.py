from rest_framework import viewsets

from employees.components import EmergencyContactComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import EmergencyContactSerializer
from employees.views.list_backed_viewset import ListBackedViewSetMixin


class EmergencyContactViewSet(ListBackedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmergencyContactComponent

    def create(self, request, *args, **kwargs):
        self.employee = self.component_class().get_employee(self.kwargs["employee_pk"])
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        # The parent check and contact list share one path for list and detail requests.
        return self.component_class().get_contacts_for_employee(
            self.kwargs["employee_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(employee=self.employee)
