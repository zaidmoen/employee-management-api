from django.db.models.deletion import ProtectedError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from employees.components import DepartmentComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = DepartmentComponent

    def get_queryset(self):
        return self.component_class().get_departments_list()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as exc:
            raise ValidationError(
                {"department": "Move or delete this department's employees first."}
            ) from exc
