# Project Requirement Checklist

This file maps the assignment requirements to the implementation so the project is easier to review.

| Requirement | Implementation |
| --- | --- |
| Django, Django REST Framework, and MySQL | `employee_api/settings.py`, `requirements.txt`, `database/create_database.sql` |
| Employee and Department models | `employees/models/` |
| One department to many employees | `Employee.department` foreign key with `related_name="employees"` |
| Database constraints and indexes | `Employee.Meta` and migrations |
| Initial, schema, and data migrations | `employees/migrations/0001`, `0002`, and `0003` |
| Employee CRUD | `EmployeeViewSet` and router URLs |
| Department CRUD and counts | `DepartmentViewSet` with database annotations |
| Filtering, search, and ordering | Employee component and repository |
| Validation | `employees/serializers/` |
| Authentication | DRF token and session authentication |
| Regular and admin access levels | `IsAuthenticatedAndAdminWrite` |
| Employee transfer transaction | `employees/components/employee_component.py` |
| Separated business logic | Controllers, components, and repositories are separate |
| Automated tests | `employees/tests/` |
| N+1 optimization | `select_related("department")` and query-count test |
| Documentation and examples | `README.md` and `docs/api_examples.http` |

## Final verification commands

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py check
python manage.py test --settings=employee_api.test_settings
```
