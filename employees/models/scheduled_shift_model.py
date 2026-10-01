from django.db import models

from .employee_model import Employee


class ScheduledShift(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="scheduled_shifts",
        db_index=False,
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_datetime"]
        indexes = [
            models.Index(
                fields=["employee", "start_datetime"],
                name="shift_employee_start_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_datetime__gt=models.F("start_datetime")),
                name="shift_end_after_start",
            ),
        ]

    def __str__(self):
        return f"Shift {self.pk} for employee {self.employee_id}"
