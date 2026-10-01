from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from employees.components import DepartmentComponent, EmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.employee_serializer import EmployeeOutputSchema


class DepartmentEmployeeViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent
    http_method_names = ["get", "post", "head", "options"]

    def list(self, request, department_pk=None):
        records = self.component_class().get_employees_for_department(int(department_pk))
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(records, request, view=self)
        return paginator.get_paginated_response(EmployeeOutputSchema(many=True).dump(page))

    def create(self, request, department_pk=None):
        DepartmentComponent().get_department(int(department_pk))
        employee = self.component_class().create_employee(request.data, department_override=int(department_pk))
        return Response(EmployeeOutputSchema().dump(employee), status=status.HTTP_201_CREATED)

    def retrieve(self, request, department_pk=None, pk=None):
        records = self.component_class().get_employees_for_department(int(department_pk))
        for employee in records:
            if employee.id == int(pk):
                return Response(EmployeeOutputSchema().dump(employee))
        raise NotFound("The requested resource does not exist under this department.")
