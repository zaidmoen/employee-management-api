from datetime import date

from django.core.management.base import BaseCommand
from sqlalchemy import select

from employees.models.sqlalchemy_models import DepartmentRecord, EmployeeRecord
from employees.sqlalchemy_db import SessionLocal


class Command(BaseCommand):
    help = "Create a few departments and employees for local testing"

    def handle(self, *args, **options):
        with SessionLocal.begin() as session:
            engineering = self._get_or_create_department(
                session,
                "Engineering",
                "Software and infrastructure team",
            )
            human_resources = self._get_or_create_department(
                session,
                "Human Resources",
                "People operations team",
            )
            self._get_or_create_employee(
                session,
                email="lina@example.com",
                first_name="Lina",
                last_name="Haddad",
                phone_number="+970 599 000 001",
                hire_date=date(2024, 2, 10),
                department_id=engineering.id,
            )
            self._get_or_create_employee(
                session,
                email="samer@example.com",
                first_name="Samer",
                last_name="Nassar",
                phone_number="+970 599 000 002",
                hire_date=date(2023, 7, 1),
                department_id=human_resources.id,
            )
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))

    @staticmethod
    def _get_or_create_department(session, name, description):
        department = session.scalar(
            select(DepartmentRecord).where(DepartmentRecord.name == name)
        )
        if department is None:
            department = DepartmentRecord(name=name, description=description)
            session.add(department)
            session.flush()
        return department

    @staticmethod
    def _get_or_create_employee(session, **values):
        employee = session.scalar(
            select(EmployeeRecord).where(EmployeeRecord.email == values["email"])
        )
        if employee is None:
            session.add(EmployeeRecord(**values))
