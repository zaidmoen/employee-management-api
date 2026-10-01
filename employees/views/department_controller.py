from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from employees.components import DepartmentComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.department_serializer import DepartmentOutputSchema


class DepartmentViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = DepartmentComponent

    def list(self, request):
        records = self.component_class().get_departments_list()
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(records, request, view=self)
        return paginator.get_paginated_response(DepartmentOutputSchema(many=True).dump(page))

    def create(self, request):
        department = self.component_class().create_department(request.data)
        return Response(DepartmentOutputSchema().dump(department), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        department = self.component_class().get_department(int(pk))
        return Response(DepartmentOutputSchema().dump(department))

    def update(self, request, pk=None):
        department = self.component_class().update_department(int(pk), request.data, partial=False)
        return Response(DepartmentOutputSchema().dump(department))

    def partial_update(self, request, pk=None):
        department = self.component_class().update_department(int(pk), request.data, partial=True)
        return Response(DepartmentOutputSchema().dump(department))

    def destroy(self, request, pk=None):
        self.component_class().delete_department(int(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
