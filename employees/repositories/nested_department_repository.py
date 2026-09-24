from django.db import connection

from employees.models import Department


class NestedDepartmentRepository:
    def get_by_id(self, department_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, description, created_at, updated_at
                FROM employees_department
                WHERE id = %s
                """,
                [department_id],
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return Department(
            id=row[0],
            name=row[1],
            description=row[2],
            created_at=row[3],
            updated_at=row[4],
        )
