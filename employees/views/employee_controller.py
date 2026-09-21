from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from employees.components import EmployeeComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers import EmployeeSerializer, EmployeeTransferSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = EmployeeComponent

    def get_queryset(self):
        return self.component_class().get_employees_list(self.request.query_params)

    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        input_serializer = EmployeeTransferSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        employee = self.component_class().transfer_employee(
            pk,
            input_serializer.validated_data["department"],
        )
        return Response(self.get_serializer(employee).data, status=status.HTTP_200_OK)
