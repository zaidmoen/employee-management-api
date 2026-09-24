from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components import NestedEmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import NestedEmployeeSerializer
from employees.views.list_backed_viewset import ListBackedViewSetMixin


class DepartmentEmployeeViewSet(ListBackedViewSetMixin, viewsets.ViewSet):
    serializer_class = NestedEmployeeSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = NestedEmployeeComponent

    def get_object_list(self):
        return self.component_class().get_employees_for_department(
            self.kwargs["department_pk"]
        )

    def list(self, request, department_pk=None):
        employees = self.get_object_list()
        return self.get_list_response(request, employees, self.serializer_class)

    def create(self, request, department_pk=None):
        component = self.component_class()
        department = component.get_department(department_pk)
        input_serializer = self.serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        employee = component.create_employee(
            department,
            input_serializer.validated_data,
        )
        return Response(
            self.serializer_class(employee).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None, department_pk=None):
        employee = self.get_object()
        return Response(self.serializer_class(employee).data)
