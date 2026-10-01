from marshmallow import ValidationError as MarshmallowValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from employees.components.shift_component import ShiftComponent
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.shift_serializer import (
    ForecastQuerySchema,
    ShiftListQuerySchema,
    ShiftOutputSchema,
)


def load_query(schema_class, params):
    try:
        return schema_class().load(params)
    except MarshmallowValidationError as exc:
        raise ValidationError(exc.messages) from exc


def shift_response(shift, status_code=status.HTTP_200_OK):
    return Response(ShiftOutputSchema().dump(shift), status=status_code)


class EmployeeShiftListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = ShiftComponent

    def get(self, request, employee_id):
        component = self.component_class()
        component.list_shifts(employee_id)  # Check the parent before query validation.
        filters = load_query(ShiftListQuerySchema, request.query_params)
        shifts = component.list_shifts(
            employee_id, filters.get("from_date"), filters.get("to_date")
        )
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(shifts, request, view=self)
        data = ShiftOutputSchema(many=True).dump(page)
        return paginator.get_paginated_response(data)

    def post(self, request, employee_id):
        shift = self.component_class().create_shift(employee_id, request.data)
        return shift_response(shift, status.HTTP_201_CREATED)


class ScheduledShiftDetailView(APIView):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = ShiftComponent

    def get(self, request, shift_id):
        return shift_response(self.component_class().get_shift(shift_id))

    def patch(self, request, shift_id):
        shift = self.component_class().update_shift(shift_id, request.data)
        return shift_response(shift)

    def delete(self, request, shift_id):
        self.component_class().delete_shift(shift_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ForecastedPayView(APIView):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    component_class = ShiftComponent

    def get(self, request, employee_id):
        component = self.component_class()
        component.list_shifts(employee_id)  # A missing employee wins over bad query values.
        filters = load_query(ForecastQuerySchema, request.query_params)
        summary = component.forecast_summary(
            employee_id, filters["from_date"], filters["to_date"]
        )
        return Response(summary)
