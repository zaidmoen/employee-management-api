from sqlalchemy import case, func, select

from employees.models.sqlalchemy_models import DepartmentRecord, EmployeeRecord


class DepartmentRepository:
    def get_all_with_employee_counts(self, session):
        statement = (
            select(
                DepartmentRecord,
                func.count(EmployeeRecord.id).label("employee_count"),
                func.sum(case((EmployeeRecord.is_active.is_(True), 1), else_=0)).label("active_employee_count"),
            )
            .outerjoin(EmployeeRecord, EmployeeRecord.department_id == DepartmentRecord.id)
            .group_by(DepartmentRecord.id)
            .order_by(DepartmentRecord.name)
        )
        results = []
        for department, total, active in session.execute(statement):
            department.employee_count = total or 0
            department.active_employee_count = active or 0
            results.append(department)
        return results

    def get_by_id(self, session, department_id):
        department = session.get(DepartmentRecord, department_id)
        if department is not None:
            department.employee_count = session.scalar(
                select(func.count(EmployeeRecord.id)).where(
                    EmployeeRecord.department_id == department_id
                )
            ) or 0
            department.active_employee_count = session.scalar(
                select(func.count(EmployeeRecord.id)).where(
                    EmployeeRecord.department_id == department_id,
                    EmployeeRecord.is_active.is_(True),
                )
            ) or 0
        return department

    def create(self, session, values):
        department = DepartmentRecord(**values)
        session.add(department)
        session.flush()
        return department

    def has_employees(self, session, department_id):
        return session.scalar(select(EmployeeRecord.id).where(EmployeeRecord.department_id == department_id).limit(1)) is not None
