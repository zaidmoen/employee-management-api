from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import (
    DepartmentEmployeeViewSet,
    DepartmentViewSet,
    EmergencyContactViewSet,
    EmployeeViewSet,
    EmployeeShiftListCreateView,
    ForecastedPayView,
    ScheduledShiftDetailView,
)
from django.urls import path


router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("departments", DepartmentViewSet, basename="department")

# Nested routers add the parent id to the route kwargs for each child viewset.
department_router = NestedSimpleRouter(router, "departments", lookup="department")
department_router.register(
    "employees",
    DepartmentEmployeeViewSet,
    basename="department-employees",
)

employee_router = NestedSimpleRouter(router, "employees", lookup="employee")
employee_router.register(
    "contacts",
    EmergencyContactViewSet,
    basename="employee-contacts",
)

urlpatterns = [
    path(
        "employees/<int:employee_id>/shifts/",
        EmployeeShiftListCreateView.as_view(),
        name="employee-shifts",
    ),
    path(
        "employees/<int:employee_id>/forecasted-pay/",
        ForecastedPayView.as_view(),
        name="employee-forecasted-pay",
    ),
    path("shifts/<int:shift_id>/", ScheduledShiftDetailView.as_view(), name="shift-detail"),
] + router.urls + department_router.urls + employee_router.urls
