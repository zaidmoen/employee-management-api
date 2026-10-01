from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("employees", "0006_scheduled_shift")]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="ScheduledShift"),
                migrations.DeleteModel(name="EmergencyContact"),
                migrations.DeleteModel(name="Employee"),
                migrations.DeleteModel(name="Department"),
            ],
        ),
    ]
