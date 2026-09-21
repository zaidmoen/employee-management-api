from rest_framework import serializers

from employees.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(read_only=True)
    active_employee_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = [
            "id", "name", "description", "employee_count",
            "active_employee_count", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        cleaned_name = value.strip()
        if len(cleaned_name) < 2:
            raise serializers.ValidationError("Department name must have at least 2 characters.")
        return cleaned_name
