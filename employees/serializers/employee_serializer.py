import re
from datetime import date

from rest_framework import serializers

from employees.models import Department, Employee


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id", "first_name", "last_name", "full_name", "email",
            "phone_number", "hire_date", "is_active", "department",
            "department_name", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "department": {"error_messages": {
                "does_not_exist": "The selected department does not exist."
            }}
        }

    def validate_email(self, value):
        cleaned_email = value.strip().lower()
        matches = Employee.objects.filter(email__iexact=cleaned_email)
        if self.instance:
            matches = matches.exclude(pk=self.instance.pk)
        if matches.exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return cleaned_email

    def validate_phone_number(self, value):
        if value and not re.fullmatch(r"[0-9+()\- ]{7,25}", value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value.strip()

    def validate_hire_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Hire date cannot be in the future.")
        return value

    def validate(self, attrs):
        for field in ("first_name", "last_name"):
            if field in attrs:
                attrs[field] = attrs[field].strip()
                if not attrs[field]:
                    raise serializers.ValidationError({field: "This field cannot be blank."})
        return attrs


class EmployeeTransferSerializer(serializers.Serializer):
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        error_messages={
            "does_not_exist": "The target department does not exist.",
            "incorrect_type": "Department id must be an integer.",
        },
    )
