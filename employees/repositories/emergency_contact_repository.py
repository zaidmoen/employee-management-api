from sqlalchemy import select

from employees.models.sqlalchemy_models import EmergencyContactRecord


class EmergencyContactRepository:
    def get_for_employee(self, session, employee_id):
        statement = select(EmergencyContactRecord).where(EmergencyContactRecord.employee_id == employee_id).order_by(EmergencyContactRecord.name, EmergencyContactRecord.id)
        return list(session.scalars(statement))

    def get_by_id(self, session, contact_id):
        return session.get(EmergencyContactRecord, contact_id)

    def create_for_employee(self, session, employee_id, contact_data):
        contact = EmergencyContactRecord(employee_id=employee_id, **contact_data)
        session.add(contact)
        session.flush()
        return contact
