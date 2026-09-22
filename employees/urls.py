from django.urls import path

from .views import DepartmentViewSet, EmployeeViewSet


employee_list = EmployeeViewSet.as_view({
    "get": "list",
    "post": "create",
})

employee_detail = EmployeeViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

employee_transfer = EmployeeViewSet.as_view({
    "post": "transfer",
})

department_list = DepartmentViewSet.as_view({
    "get": "list",
    "post": "create",
})

department_detail = DepartmentViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})


urlpatterns = [
    # GET /api/employees/ -> list employees
    # POST /api/employees/ -> create employee
    path("employees/", employee_list, name="employee-list"),

    # GET /api/employees/<id>/ -> get one employee
    # PUT/PATCH /api/employees/<id>/ -> update employee
    # DELETE /api/employees/<id>/ -> delete employee
    path("employees/<int:pk>/", employee_detail, name="employee-detail"),

    # POST /api/employees/<id>/transfer/ -> move employee to another department
    path(
        "employees/<int:pk>/transfer/",
        employee_transfer,
        name="employee-transfer",
    ),

    # GET /api/departments/ -> list departments
    # POST /api/departments/ -> create department
    path("departments/", department_list, name="department-list"),

    # GET /api/departments/<id>/ -> get one department
    # PUT/PATCH /api/departments/<id>/ -> update department
    # DELETE /api/departments/<id>/ -> delete department
    path("departments/<int:pk>/", department_detail, name="department-detail"),
]
