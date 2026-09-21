from django.db import models

from .department_model import Department


class Employee(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=25, blank=True)
    hire_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["department", "is_active"], name="emp_dept_active_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(first_name=""),
                name="employee_first_name_not_empty",
            ),
            models.CheckConstraint(
                condition=~models.Q(last_name=""),
                name="employee_last_name_not_empty",
            ),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.email})"
