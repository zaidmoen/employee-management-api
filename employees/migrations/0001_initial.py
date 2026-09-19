import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=80)),
                ("last_name", models.CharField(max_length=80)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("hire_date", models.DateField(db_index=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="employees",
                        to="employees.department",
                    ),
                ),
            ],
            options={"ordering": ["last_name", "first_name"]},
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(
                condition=models.Q(("first_name", ""), _negated=True),
                name="employee_first_name_not_empty",
            ),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(
                condition=models.Q(("last_name", ""), _negated=True),
                name="employee_last_name_not_empty",
            ),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["department", "is_active"], name="emp_dept_active_idx"),
        ),
    ]

