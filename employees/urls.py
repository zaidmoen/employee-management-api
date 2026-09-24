from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentEmployeeViewSet,
    DepartmentViewSet,
    EmergencyContactViewSet,
    EmployeeViewSet,
)


router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("departments", DepartmentViewSet, basename="department")

department_employee_list = DepartmentEmployeeViewSet.as_view({
    "get": "list",
    "post": "create",
})
department_employee_detail = DepartmentEmployeeViewSet.as_view({
    "get": "retrieve",
})
employee_contact_list = EmergencyContactViewSet.as_view({
    "get": "list",
    "post": "create",
})
employee_contact_detail = EmergencyContactViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
    "delete": "destroy",
})

# These explicit paths keep the parent id visible without an extra router package.
urlpatterns = router.urls + [
    path(
        "departments/<int:department_pk>/employees/",
        department_employee_list,
        name="department-employees-list",
    ),
    path(
        "departments/<int:department_pk>/employees/<int:pk>/",
        department_employee_detail,
        name="department-employees-detail",
    ),
    path(
        "employees/<int:employee_pk>/contacts/",
        employee_contact_list,
        name="employee-contacts-list",
    ),
    path(
        "employees/<int:employee_pk>/contacts/<int:pk>/",
        employee_contact_detail,
        name="employee-contacts-detail",
    ),
]
