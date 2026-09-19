from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, EmployeeViewSet


router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("departments", DepartmentViewSet, basename="department")

urlpatterns = router.urls

