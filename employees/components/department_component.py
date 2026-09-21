from employees.repositories import DepartmentRepository


class DepartmentComponent:
    def __init__(self, repository=None):
        self.repository = repository or DepartmentRepository()

    def get_departments_list(self):
        return self.repository.get_all_with_employee_counts()
