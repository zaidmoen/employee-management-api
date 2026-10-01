from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from employees.components import EmergencyContactComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.emergency_contact_serializer import EmergencyContactOutputSchema


class EmergencyContactViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmergencyContactComponent

    def list(self, request, employee_pk=None):
        records = self.component_class().get_contacts_for_employee(int(employee_pk))
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(records, request, view=self)
        return paginator.get_paginated_response(EmergencyContactOutputSchema(many=True).dump(page))

    def create(self, request, employee_pk=None):
        contact = self.component_class().create_contact(int(employee_pk), request.data)
        return Response(EmergencyContactOutputSchema().dump(contact), status=status.HTTP_201_CREATED)

    def retrieve(self, request, employee_pk=None, pk=None):
        contact = self.component_class().get_contact(int(employee_pk), int(pk))
        return Response(EmergencyContactOutputSchema().dump(contact))

    def update(self, request, employee_pk=None, pk=None):
        contact = self.component_class().update_contact(int(employee_pk), int(pk), request.data, partial=False)
        return Response(EmergencyContactOutputSchema().dump(contact))

    def partial_update(self, request, employee_pk=None, pk=None):
        contact = self.component_class().update_contact(int(employee_pk), int(pk), request.data, partial=True)
        return Response(EmergencyContactOutputSchema().dump(contact))

    def destroy(self, request, employee_pk=None, pk=None):
        self.component_class().delete_contact(int(employee_pk), int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
