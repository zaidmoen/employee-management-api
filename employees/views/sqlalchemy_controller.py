"""DRF routes, permissions, and responses for SQLAlchemy-backed records."""
from marshmallow import ValidationError as MarshmallowError
from sqlalchemy.exc import IntegrityError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from employees.components.sqlalchemy_component import EmployeeComponent
from employees.database import session_scope
from employees.permissions import IsAuthenticatedAndAdminWrite
from employees.serializers.schemas import (
    ContactInput, ContactSchema, DepartmentInput, DepartmentSchema,
    EmployeeInput, EmployeeSchema,
)
from employees.sqlalchemy_models import Department, Employee, EmergencyContact


class ApiViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedAndAdminWrite]
    pagination_class = PageNumberPagination

    def parse(self, schema, data, partial=False):
        try:
            return schema.load(data, partial=partial)
        except MarshmallowError as exc:
            raise ValidationError(exc.messages) from exc

    def page(self, request, items, schema):
        paginator = self.pagination_class()
        selected = paginator.paginate_queryset(items, request, view=self)
        return paginator.get_paginated_response(schema.dump(selected, many=True))

    def conflict(self, exc):
        # Unique constraints may also fail when another request inserts at the same time.
        raise ValidationError({"detail": "Duplicate value or invalid relation."}) from exc


class DepartmentViewSet(ApiViewSet):
    def list(self, request):
        with session_scope() as session:
            return self.page(request, EmployeeComponent(session).repo.list_departments(), DepartmentSchema())

    def retrieve(self, request, pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            department = component.require(Department, pk)
            department.employee_count = len(department.employees)
            department.active_employee_count = sum(e.is_active for e in department.employees)
            return Response(DepartmentSchema().dump(department))

    def create(self, request):
        data = self.parse(DepartmentInput(), request.data)
        try:
            with session_scope() as session:
                repo = EmployeeComponent(session).repo
                if repo.department_name_exists(data["name"]):
                    raise ValidationError({"name": "Department already exists."})
                department = repo.add(Department(**data))
                return Response(DepartmentSchema().dump(department), status=201)
        except IntegrityError as exc:
            self.conflict(exc)

    def update(self, request, pk=None, partial=False):
        data = self.parse(DepartmentInput(), request.data, partial=partial)
        try:
            with session_scope() as session:
                component = EmployeeComponent(session)
                department = component.require(Department, pk)
                if "name" in data and component.repo.department_name_exists(data["name"], department.id):
                    raise ValidationError({"name": "Department already exists."})
                for key, value in data.items():
                    setattr(department, key, value)
                session.flush()
                return Response(DepartmentSchema().dump(department))
        except IntegrityError as exc:
            self.conflict(exc)

    def partial_update(self, request, pk=None):
        return self.update(request, pk, partial=True)

    def destroy(self, request, pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            department = component.require(Department, pk)
            if department.employees:
                raise ValidationError({"department": "Move or delete this department's employees first."})
            component.repo.delete(department)
            return Response(status=204)


class EmployeeViewSet(ApiViewSet):
    def list(self, request):
        with session_scope() as session:
            return self.page(request, EmployeeComponent(session).list_employees(request.query_params), EmployeeSchema())

    def retrieve(self, request, pk=None):
        with session_scope() as session:
            return Response(EmployeeSchema().dump(EmployeeComponent(session).require(Employee, pk)))

    def create(self, request):
        data = self.parse(EmployeeInput(), request.data)
        try:
            with session_scope() as session:
                employee = EmployeeComponent(session).save_employee(data)
                return Response(EmployeeSchema().dump(employee), status=201)
        except IntegrityError as exc:
            self.conflict(exc)

    def update(self, request, pk=None, partial=False):
        data = self.parse(EmployeeInput(), request.data, partial=partial)
        try:
            with session_scope() as session:
                component = EmployeeComponent(session)
                employee = component.save_employee(data, component.require(Employee, pk))
                return Response(EmployeeSchema().dump(employee))
        except IntegrityError as exc:
            self.conflict(exc)

    def partial_update(self, request, pk=None):
        return self.update(request, pk, partial=True)

    def destroy(self, request, pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            component.repo.delete(component.require(Employee, pk))
            return Response(status=204)

    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None):
        department_id = request.data.get("department_id")
        if isinstance(department_id, bool) or not str(department_id).isdigit():
            raise ValidationError({"department_id": "Department id must be an integer."})
        with session_scope() as session:
            employee = EmployeeComponent(session).transfer(pk, int(department_id))
            return Response(EmployeeSchema().dump(employee))


class DepartmentEmployeeViewSet(ApiViewSet):
    http_method_names = ["get", "post", "head", "options"]

    def list(self, request, department_pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            component.require(Department, department_pk)
            items = component.list_employees(request.query_params, department_id=department_pk)
            return self.page(request, items, EmployeeSchema())

    def retrieve(self, request, pk=None, department_pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            component.require(Department, department_pk)
            employee = component.require(Employee, pk)
            if employee.department_id != int(department_pk):
                from rest_framework.exceptions import NotFound
                raise NotFound("Employee does not belong to this department.")
            return Response(EmployeeSchema().dump(employee))

    def create(self, request, department_pk=None):
        with session_scope() as session:
            EmployeeComponent(session).require(Department, department_pk)
        payload = dict(request.data.items())
        payload["department"] = int(department_pk)
        data = self.parse(EmployeeInput(), payload)
        try:
            with session_scope() as session:
                employee = EmployeeComponent(session).save_employee(data)
                return Response(EmployeeSchema().dump(employee), status=201)
        except IntegrityError as exc:
            self.conflict(exc)


class EmergencyContactViewSet(ApiViewSet):
    def parent(self, component, employee_pk):
        return component.require(Employee, employee_pk)

    def contact(self, component, employee_pk, pk):
        self.parent(component, employee_pk)
        contact = component.require(EmergencyContact, pk)
        if contact.employee_id != int(employee_pk):
            from rest_framework.exceptions import NotFound
            raise NotFound("Contact does not belong to this employee.")
        return contact

    def list(self, request, employee_pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            self.parent(component, employee_pk)
            return self.page(request, component.repo.list_contacts(int(employee_pk)), ContactSchema())

    def retrieve(self, request, pk=None, employee_pk=None):
        with session_scope() as session:
            return Response(ContactSchema().dump(self.contact(EmployeeComponent(session), employee_pk, pk)))

    def create(self, request, employee_pk=None):
        data = self.parse(ContactInput(), request.data)
        with session_scope() as session:
            component = EmployeeComponent(session)
            parent = self.parent(component, employee_pk)
            contact = component.repo.add(EmergencyContact(employee=parent, **data))
            return Response(ContactSchema().dump(contact), status=201)

    def update(self, request, pk=None, employee_pk=None, partial=False):
        data = self.parse(ContactInput(), request.data, partial=partial)
        with session_scope() as session:
            component = EmployeeComponent(session)
            contact = self.contact(component, employee_pk, pk)
            for key, value in data.items():
                setattr(contact, key, value)
            session.flush()
            return Response(ContactSchema().dump(contact))

    def partial_update(self, request, pk=None, employee_pk=None):
        return self.update(request, pk, employee_pk, partial=True)

    def destroy(self, request, pk=None, employee_pk=None):
        with session_scope() as session:
            component = EmployeeComponent(session)
            component.repo.delete(self.contact(component, employee_pk, pk))
            return Response(status=204)
