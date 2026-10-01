from sqlalchemy import or_, select

from employees.models.sqlalchemy_models import DepartmentRecord, EmployeeRecord, ScheduledShiftRecord


class EmployeeRepository:
    def get_all(self, session):
        return self._with_department(select(EmployeeRecord).order_by(EmployeeRecord.last_name, EmployeeRecord.first_name), session)

    def get_for_department(self, session, department_id):
        statement = select(EmployeeRecord).where(EmployeeRecord.department_id == department_id).order_by(EmployeeRecord.last_name, EmployeeRecord.first_name)
        return self._with_department(statement, session)

    def filter(self, session, active=None, department_id=None, search=None, ordering=None):
        statement = select(EmployeeRecord)
        if active is not None:
            statement = statement.where(EmployeeRecord.is_active == active)
        if department_id:
            statement = statement.where(EmployeeRecord.department_id == department_id)
        if search:
            value = f"%{search.strip()}%"
            statement = statement.where(or_(EmployeeRecord.first_name.ilike(value), EmployeeRecord.last_name.ilike(value), EmployeeRecord.email.ilike(value)))
        if ordering:
            descending = ordering.startswith("-")
            column = getattr(EmployeeRecord, ordering.removeprefix("-"))
            statement = statement.order_by(column.desc() if descending else column.asc())
        else:
            statement = statement.order_by(EmployeeRecord.last_name, EmployeeRecord.first_name)
        return self._with_department(statement, session)

    def get_by_id(self, session, employee_id, lock=False):
        statement = select(EmployeeRecord).where(EmployeeRecord.id == employee_id)
        if lock:
            statement = statement.with_for_update()
        employee = session.scalar(statement)
        if employee is not None:
            employee.department_name = session.scalar(select(DepartmentRecord.name).where(DepartmentRecord.id == employee.department_id))
        return employee

    def get_email_match(self, session, email, exclude_id=None):
        statement = select(EmployeeRecord.id).where(EmployeeRecord.email.ilike(email))
        if exclude_id is not None:
            statement = statement.where(EmployeeRecord.id != exclude_id)
        return session.scalar(statement.limit(1))

    def create(self, session, values):
        employee = EmployeeRecord(**values)
        session.add(employee)
        session.flush()
        return employee

    def has_shifts(self, session, employee_id):
        return session.scalar(select(ScheduledShiftRecord.id).where(ScheduledShiftRecord.employee_id == employee_id).limit(1)) is not None

    @staticmethod
    def _with_department(statement, session):
        employees = list(session.scalars(statement))
        ids = {employee.department_id for employee in employees}
        names = dict(
            session.execute(
                select(DepartmentRecord.id, DepartmentRecord.name).where(
                    DepartmentRecord.id.in_(ids)
                )
            ).all()
        ) if ids else {}
        for employee in employees:
            employee.department_name = names.get(employee.department_id, "")
        return employees
