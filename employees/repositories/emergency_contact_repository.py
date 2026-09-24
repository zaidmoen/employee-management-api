from django.db import connection
from django.utils import timezone

from employees.models import Employee, EmergencyContact


class EmergencyContactRepository:
    def get_employee(self, employee_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, first_name, last_name, email, phone_number, hire_date,
                       is_active, department_id, created_at, updated_at
                FROM employees_employee
                WHERE id = %s
                """,
                [employee_id],
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return Employee(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            email=row[3],
            phone_number=row[4],
            hire_date=row[5],
            is_active=row[6],
            department_id=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    def get_for_employee(self, employee_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, relationship, phone_number, email,
                       created_at, updated_at, employee_id
                FROM employees_emergencycontact
                WHERE employee_id = %s
                ORDER BY name, id
                """,
                [employee_id],
            )
            rows = cursor.fetchall()

        return [
            EmergencyContact(
                id=row[0],
                name=row[1],
                relationship=row[2],
                phone_number=row[3],
                email=row[4],
                created_at=row[5],
                updated_at=row[6],
                employee_id=row[7],
            )
            for row in rows
        ]

    def create_for_employee(self, employee, contact_data):
        now = connection.ops.adapt_datetimefield_value(timezone.now())
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employees_emergencycontact
                    (name, relationship, phone_number, email,
                     created_at, updated_at, employee_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    contact_data["name"],
                    contact_data["relationship"],
                    contact_data["phone_number"],
                    contact_data["email"],
                    now,
                    now,
                    employee.id,
                ],
            )
            contact_id = cursor.lastrowid

        return EmergencyContact(
            id=contact_id,
            name=contact_data["name"],
            relationship=contact_data["relationship"],
            phone_number=contact_data["phone_number"],
            email=contact_data["email"],
            created_at=now,
            updated_at=now,
            employee_id=employee.id,
        )

    def update_for_employee(self, employee_id, contact, changes):
        allowed_fields = {"name", "relationship", "phone_number", "email"}
        changes = {key: value for key, value in changes.items() if key in allowed_fields}
        now = connection.ops.adapt_datetimefield_value(timezone.now())

        if changes:
            assignments = ", ".join(f"{field} = %s" for field in changes)
            values = list(changes.values()) + [now, contact.id, employee_id]
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE employees_emergencycontact
                    SET {assignments}, updated_at = %s
                    WHERE id = %s AND employee_id = %s
                    """,
                    values,
                )
                if cursor.rowcount == 0:
                    return None

            for field, value in changes.items():
                setattr(contact, field, value)
            contact.updated_at = now

        return contact

    def delete_for_employee(self, employee_id, contact_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM employees_emergencycontact
                WHERE id = %s AND employee_id = %s
                """,
                [contact_id, employee_id],
            )
            return cursor.rowcount > 0
