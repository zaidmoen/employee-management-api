from django.db import connection
from django.utils import timezone

from employees.models import Employee


class NestedEmployeeRepository:
    def get_for_department(self, department_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT employee.id, employee.first_name, employee.last_name,
                       employee.email, employee.phone_number, employee.hire_date,
                       employee.is_active, employee.department_id,
                       employee.created_at, employee.updated_at, department.name
                FROM employees_employee AS employee
                JOIN employees_department AS department
                  ON department.id = employee.department_id
                WHERE employee.department_id = %s
                ORDER BY employee.last_name, employee.first_name, employee.id
                """,
                [department_id],
            )
            rows = cursor.fetchall()

        employees = []
        for row in rows:
            employee = Employee(
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
            employee.department_name = row[10]
            employees.append(employee)

        return employees

    def email_exists(self, email):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM employees_employee WHERE LOWER(email) = LOWER(%s)",
                [email],
            )
            return cursor.fetchone() is not None

    def create_for_department(self, department, employee_data):
        now = connection.ops.adapt_datetimefield_value(timezone.now())
        phone_number = employee_data.get("phone_number", "")
        is_active = employee_data.get("is_active", True)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO employees_employee
                    (first_name, last_name, email, phone_number, hire_date,
                     is_active, department_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    employee_data["first_name"],
                    employee_data["last_name"],
                    employee_data["email"],
                    phone_number,
                    employee_data["hire_date"],
                    is_active,
                    department.id,
                    now,
                    now,
                ],
            )
            employee_id = cursor.lastrowid

        employee = Employee(
            id=employee_id,
            first_name=employee_data["first_name"],
            last_name=employee_data["last_name"],
            email=employee_data["email"],
            phone_number=phone_number,
            hire_date=employee_data["hire_date"],
            is_active=is_active,
            department_id=department.id,
            created_at=now,
            updated_at=now,
        )
        employee.department_name = department.name
        return employee
