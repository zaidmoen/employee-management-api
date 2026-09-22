from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    # Django admin panel
    path("admin/", admin.site.urls),

    # POST /api/token/ -> get authentication token
    path("api/token/", obtain_auth_token, name="api-token"),

    # Employee and department APIs start with /api/
    path("api/", include("employees.urls")),
]
