# Project Requirement Checklist

This file maps the assignment requirements to the implementation so the project is easier to review.

| Requirement | Implementation |
| --- | --- |
| Django, Django REST Framework, and MySQL | `employee_api/settings.py`, `requirements.txt`, `database/create_database.sql` |
| Employee and Department models | `employees/models.py` |
| One department to many employees | `Employee.department` foreign key with `related_name="employees"` |
| Database constraints and indexes | `Employee.Meta` and migrations |
| Initial, schema, and data migrations | `employees/migrations/0001`, `0002`, and `0003` |
| Employee CRUD | `EmployeeViewSet` and router URLs |
| Department CRUD and counts | `DepartmentViewSet` with database annotations |
| Filtering, search, and ordering | `EmployeeViewSet.get_queryset()` |
| Validation | `employees/serializers.py` |
| Authentication | DRF token and session authentication |
| Regular and admin access levels | `IsAuthenticatedAndAdminWrite` |
| Employee transfer transaction | `employees/services.py` |
| Separated business logic | Transfer rule is kept outside the view |
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
