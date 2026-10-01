import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0005_employee_hourly_rate"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScheduledShift",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                ("hourly_rate", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "employee",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="scheduled_shifts",
                        to="employees.employee",
                    ),
                ),
            ],
            options={"ordering": ["start_datetime"]},
        ),
        migrations.AddIndex(
            model_name="scheduledshift",
            index=models.Index(
                fields=["employee", "start_datetime"],
                name="shift_employee_start_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="scheduledshift",
            constraint=models.CheckConstraint(
                condition=models.Q(end_datetime__gt=models.F("start_datetime")),
                name="shift_end_after_start",
            ),
        ),
    ]
