from django.db import migrations


def normalize_existing_data(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    Department = apps.get_model("employees", "Department")

    for department in Department.objects.all().iterator():
        cleaned_name = department.name.strip()
        if cleaned_name != department.name:
            department.name = cleaned_name
            department.save(update_fields=["name"])

    for employee in Employee.objects.all().iterator():
        cleaned_email = employee.email.strip().lower()
        if cleaned_email != employee.email:
            employee.email = cleaned_email
            employee.save(update_fields=["email"])


class Migration(migrations.Migration):
    dependencies = [("employees", "0002_employee_phone_number")]

    operations = [migrations.RunPython(normalize_existing_data, migrations.RunPython.noop)]

