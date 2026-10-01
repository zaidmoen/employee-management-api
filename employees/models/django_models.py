"""Django model declarations retained for migrations, auth/admin integration.

Application CRUD uses the SQLAlchemy records in ``sqlalchemy_models.py``.
"""

from decimal import Decimal

from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=25, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    hire_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [models.Index(fields=["department", "is_active"], name="emp_dept_active_idx")]
        constraints = [
            models.CheckConstraint(condition=~models.Q(first_name=""), name="employee_first_name_not_empty"),
            models.CheckConstraint(condition=~models.Q(last_name=""), name="employee_last_name_not_empty"),
            models.CheckConstraint(condition=models.Q(hourly_rate__gte=0), name="employee_hourly_rate_non_negative"),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class EmergencyContact(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="emergency_contacts")
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=25)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class ScheduledShift(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="scheduled_shifts", db_index=False)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_datetime"]
        indexes = [models.Index(fields=["employee", "start_datetime"], name="shift_employee_start_idx")]
        constraints = [models.CheckConstraint(condition=models.Q(end_datetime__gt=models.F("start_datetime")), name="shift_end_after_start")]

    def __str__(self):
        return f"Shift {self.pk} for employee {self.employee_id}"
