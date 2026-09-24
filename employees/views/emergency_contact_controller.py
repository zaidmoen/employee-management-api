from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components import EmergencyContactComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import EmergencyContactSerializer
from employees.views.list_backed_viewset import ListBackedViewSetMixin


class EmergencyContactViewSet(ListBackedViewSetMixin, viewsets.ViewSet):
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmergencyContactComponent

    def get_object_list(self):
        return self.component_class().get_contacts_for_employee(
            self.kwargs["employee_pk"]
        )

    def list(self, request, employee_pk=None):
        contacts = self.get_object_list()
        return self.get_list_response(request, contacts, self.serializer_class)

    def create(self, request, employee_pk=None):
        component = self.component_class()
        employee = component.get_employee(employee_pk)
        input_serializer = self.serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        contact = component.create_contact(employee, input_serializer.validated_data)
        return Response(
            self.serializer_class(contact).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None, employee_pk=None):
        contact = self.get_object()
        return Response(self.serializer_class(contact).data)

    def partial_update(self, request, pk=None, employee_pk=None):
        contact = self.get_object()
        input_serializer = self.serializer_class(
            contact,
            data=request.data,
            partial=True,
        )
        input_serializer.is_valid(raise_exception=True)
        updated_contact = self.component_class().update_contact(
            employee_pk,
            contact,
            input_serializer.validated_data,
        )
        return Response(self.serializer_class(updated_contact).data)

    def destroy(self, request, pk=None, employee_pk=None):
        contact = self.get_object()
        self.component_class().delete_contact(employee_pk, contact.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
