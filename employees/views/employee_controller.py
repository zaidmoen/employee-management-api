from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from employees.components import EmployeeComponent
from employees.components.shift_component import ShiftComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.employee_serializer import (
    EmployeeOutputSchema,
    EmployeeTransferSchema,
)
from employees.components.validation import load_schema


class EmployeeViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent

    def list(self, request):
        records = self.component_class().get_employees_list(request.query_params)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(records, request, view=self)
        data = EmployeeOutputSchema(many=True).dump(page)
        return paginator.get_paginated_response(data)

    def create(self, request):
        employee = self.component_class().create_employee(request.data)
        return Response(EmployeeOutputSchema().dump(employee), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        employee = self.component_class().get_employee(int(pk))
        return Response(EmployeeOutputSchema().dump(employee))

    def update(self, request, pk=None):
        employee = self.component_class().update_employee(int(pk), request.data, partial=False)
        return Response(EmployeeOutputSchema().dump(employee))

    def partial_update(self, request, pk=None):
        employee = self.component_class().update_employee(int(pk), request.data, partial=True)
        return Response(EmployeeOutputSchema().dump(employee))

    def destroy(self, request, pk=None):
        self.component_class().delete_employee(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        values = load_schema(EmployeeTransferSchema(), request.data)
        employee = self.component_class().transfer_employee(int(pk), values["department_id"])
        return Response(EmployeeOutputSchema().dump(employee), status=status.HTTP_200_OK)
