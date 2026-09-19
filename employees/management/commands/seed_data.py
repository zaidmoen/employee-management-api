from datetime import date

from django.core.management.base import BaseCommand

from employees.models import Department, Employee


class Command(BaseCommand):
    help = "Create a few departments and employees for local testing"

    def handle(self, *args, **options):
        engineering, _ = Department.objects.get_or_create(
            name="Engineering",
            defaults={"description": "Software and infrastructure team"},
        )
        hr, _ = Department.objects.get_or_create(
            name="Human Resources",
            defaults={"description": "People operations team"},
        )

        Employee.objects.get_or_create(
            email="lina@example.com",
            defaults={
                "first_name": "Lina",
                "last_name": "Haddad",
                "phone_number": "+970 599 000 001",
                "hire_date": date(2024, 2, 10),
                "department": engineering,
            },
        )
        Employee.objects.get_or_create(
            email="samer@example.com",
            defaults={
                "first_name": "Samer",
                "last_name": "Nassar",
                "phone_number": "+970 599 000 002",
                "hire_date": date(2023, 7, 1),
                "department": hr,
            },
        )
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))

