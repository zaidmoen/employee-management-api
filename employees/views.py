from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Department, Employee
from .permissions import IsAuthenticatedAndAdminWrite
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    EmployeeTransferSerializer,
)
from .services import transfer_employee


def parse_boolean(value):
    values = {"true": True, "1": True, "false": False, "0": False}
    try:
        return values[value.lower()]
    except (AttributeError, KeyError) as exc:
        raise ValidationError({"active": "Use true, false, 1, or 0."}) from exc


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]

    def get_queryset(self):
        queryset = Employee.objects.select_related("department")
        params = self.request.query_params

        if "active" in params:
            queryset = queryset.filter(is_active=parse_boolean(params["active"]))

        if params.get("department"):
            queryset = queryset.filter(department_id=params["department"])

        if params.get("search"):
            search = params["search"].strip()
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        allowed_ordering = {"first_name", "last_name", "hire_date", "created_at"}
        ordering = params.get("ordering")
        if ordering:
            field_name = ordering.removeprefix("-")
            if field_name not in allowed_ordering:
                raise ValidationError(
                    {"ordering": f"Choose one of: {', '.join(sorted(allowed_ordering))}."}
                )
            queryset = queryset.order_by(ordering)

        return queryset

    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        input_serializer = EmployeeTransferSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        employee = transfer_employee(pk, input_serializer.validated_data["department"])
        output_serializer = self.get_serializer(employee)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]

    def get_queryset(self):
        return Department.objects.annotate(
            employee_count=Count("employees", distinct=True),
            active_employee_count=Count(
                "employees",
                filter=Q(employees__is_active=True),
                distinct=True,
            ),
        )

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as exc:
            raise ValidationError(
                {"department": "Move or delete this department's employees first."}
            ) from exc

