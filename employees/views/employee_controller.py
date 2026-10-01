from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.deletion import ProtectedError
from employees.components.shift_component import Conflict, ShiftComponent

from employees.components import EmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import EmployeeSerializer, EmployeeTransferSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent

    def get_queryset(self):
        return self.component_class().get_employees_list(self.request.query_params)

    def partial_update(self, request, *args, **kwargs):
        if "hourly_rate" not in request.data:
            return super().partial_update(request, *args, **kwargs)

        employee = self.get_object()
        other_data = request.data.copy()
        other_data.pop("hourly_rate", None)
        serializer = None
        if other_data:
            serializer = self.get_serializer(employee, data=other_data, partial=True)
            serializer.is_valid(raise_exception=True)
        ShiftComponent().update_employee_rate(employee.pk, {
            "hourly_rate": request.data["hourly_rate"],
        })
        if serializer:
            serializer.save()
        employee.refresh_from_db()
        return Response(self.get_serializer(employee).data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if "hourly_rate" not in request.data:
            return super().update(request, *args, **kwargs)

        employee = self.get_object()
        other_data = request.data.copy()
        other_data.pop("hourly_rate", None)
        other_data["hourly_rate"] = employee.hourly_rate
        serializer = self.get_serializer(employee, data=other_data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("hourly_rate", None)
        ShiftComponent().update_employee_rate(employee.pk, {
            "hourly_rate": request.data["hourly_rate"],
        })
        serializer.save()
        employee.refresh_from_db()
        return Response(self.get_serializer(employee).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        employee = self.get_object()
        if employee.scheduled_shifts.exists():
            raise Conflict({"detail": "Employee has scheduled shifts and cannot be deleted."})
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as exc:
            raise Conflict({
                "detail": "Employee has scheduled shifts and cannot be deleted."
            }) from exc

    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        input_serializer = EmployeeTransferSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        employee = self.component_class().transfer_employee(
            pk,
            input_serializer.validated_data["department"],
        )
        return Response(self.get_serializer(employee).data, status=status.HTTP_200_OK)
