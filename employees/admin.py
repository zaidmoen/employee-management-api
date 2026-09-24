from django.contrib import admin

from .models import Department, Employee, EmergencyContact


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "department", "is_active", "hire_date"]
    list_filter = ["is_active", "department"]
    search_fields = ["first_name", "last_name", "email"]
    list_select_related = ["department"]


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["name", "relationship", "employee", "phone_number", "email"]
    search_fields = ["name", "employee__first_name", "employee__last_name", "email"]
    list_select_related = ["employee"]
