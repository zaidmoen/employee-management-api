from datetime import date

from django.core.management.base import BaseCommand
from sqlalchemy import func, select

from employees.database import session_scope
from employees.sqlalchemy_models import Department, Employee


class Command(BaseCommand):
    help = "Create sample SQLAlchemy records for local API testing"

    def handle(self, *args, **options):
        with session_scope() as session:
            departments = {}
            for name, description in (("Engineering", "Software and infrastructure team"),
                                      ("Human Resources", "People operations team")):
                department = session.scalar(select(Department).where(Department.name == name))
                if department is None:
                    department = Department(name=name, description=description)
                    session.add(department)
                    session.flush()
                departments[name] = department

            for first, last, email, hired, department_name in (
                ("Lina", "Haddad", "lina@example.com", date(2024, 2, 10), "Engineering"),
                ("Samer", "Nassar", "samer@example.com", date(2023, 7, 1), "Human Resources"),
            ):
                if session.scalar(select(Employee.id).where(func.lower(Employee.email) == email)) is None:
                    session.add(Employee(first_name=first, last_name=last, email=email,
                                         hire_date=hired, department=departments[department_name]))
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
