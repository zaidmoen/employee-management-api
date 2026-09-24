from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0003_normalize_existing_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmergencyContact",
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
                ("name", models.CharField(max_length=100)),
                ("relationship", models.CharField(max_length=50)),
                ("phone_number", models.CharField(max_length=25)),
                ("email", models.EmailField(max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emergency_contacts",
                        to="employees.employee",
                    ),
                ),
            ],
            options={"ordering": ["name", "id"]},
        ),
    ]
