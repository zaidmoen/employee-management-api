from rest_framework import status, viewsets
from rest_framework.response import Response

from employees.components import DepartmentComponent, EmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import NestedEmployeeSerializer
from employees.views.list_backed_viewset import ListBackedViewSetMixin


class DepartmentEmployeeViewSet(ListBackedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = NestedEmployeeSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent
    department_component_class = DepartmentComponent
    http_method_names = ["get", "post", "head", "options"]

    def create(self, request, *args, **kwargs):
        self.department = self.department_component_class().get_department(
            self.kwargs["department_pk"]
        )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(department=self.department)

    def get_queryset(self):
        # The repository returns a list filtered by the department URL parameter.
        return self.component_class().get_employees_for_department(
            self.kwargs["department_pk"]
        )
