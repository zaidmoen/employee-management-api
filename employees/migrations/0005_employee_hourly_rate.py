from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("employees", "0004_emergency_contact")]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="hourly_rate",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                max_digits=10,
            ),
        ),
        migrations.AddConstraint(
            model_name="employee",
            constraint=models.CheckConstraint(
                condition=models.Q(hourly_rate__gte=0),
                name="employee_hourly_rate_non_negative",
            ),
        ),
    ]
