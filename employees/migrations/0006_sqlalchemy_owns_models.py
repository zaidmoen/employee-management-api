from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("employees", "0005_employee_break_minutes_employee_shift_end_and_more")]

    # Keep existing tables and records. SQLAlchemy now maps these same tables.
    # Only remove Django's model state so makemigrations does not recreate them.
    operations = [migrations.SeparateDatabaseAndState(
        database_operations=[],
        state_operations=[
            migrations.DeleteModel(name="EmergencyContact"),
            migrations.DeleteModel(name="Employee"),
            migrations.DeleteModel(name="Department"),
        ],
    )]
