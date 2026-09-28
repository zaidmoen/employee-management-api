"""Only SQLAlchemy reads and writes belong here."""
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload

from employees.sqlalchemy_models import Department, Employee, EmergencyContact


class Repository:
    def __init__(self, session):
        self.session = session

    def get(self, model, item_id, *, lock=False):
        statement = select(model).where(model.id == item_id)
        if model is Employee:
            statement = statement.options(joinedload(Employee.department))
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def list_departments(self):
        statement = select(Department).order_by(Department.name)
        departments = list(self.session.scalars(statement))
        counts = self.session.execute(
            select(Employee.department_id, func.count(Employee.id),
                   func.sum(Employee.is_active))
            .group_by(Employee.department_id)
        ).all()
        totals = {item_id: (count, active or 0) for item_id, count, active in counts}
        for department in departments:
            department.employee_count, department.active_employee_count = totals.get(department.id, (0, 0))
        return departments

    def list_employees(self, active=None, department_id=None, search=None, ordering=None):
        statement = select(Employee).options(joinedload(Employee.department))
        if active is not None:
            statement = statement.where(Employee.is_active == active)
        if department_id is not None:
            statement = statement.where(Employee.department_id == department_id)
        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(or_(Employee.first_name.ilike(pattern),
                                           Employee.last_name.ilike(pattern),
                                           Employee.email.ilike(pattern)))
        if ordering:
            field = getattr(Employee, ordering.lstrip("-"))
            statement = statement.order_by(field.desc() if ordering.startswith("-") else field)
        else:
            statement = statement.order_by(Employee.last_name, Employee.first_name)
        return list(self.session.scalars(statement))

    def list_contacts(self, employee_id):
        return list(self.session.scalars(
            select(EmergencyContact).where(EmergencyContact.employee_id == employee_id)
            .order_by(EmergencyContact.name, EmergencyContact.id)
        ))

    def email_exists(self, email, excluding=None):
        statement = select(Employee.id).where(func.lower(Employee.email) == email.lower())
        if excluding is not None:
            statement = statement.where(Employee.id != excluding)
        return self.session.scalar(statement) is not None

    def department_name_exists(self, name, excluding=None):
        statement = select(Department.id).where(Department.name == name)
        if excluding is not None:
            statement = statement.where(Department.id != excluding)
        return self.session.scalar(statement) is not None

    def add(self, item):
        self.session.add(item)
        self.session.flush()
        return item

    def delete(self, item):
        self.session.delete(item)
        self.session.flush()
