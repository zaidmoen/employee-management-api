import re
from datetime import date

from rest_framework import serializers


class NestedEmployeeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=80)
    last_name = serializers.CharField(max_length=80)
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=25, required=False, allow_blank=True)
    hire_date = serializers.DateField()
    is_active = serializers.BooleanField(required=False, default=True)
    department = serializers.IntegerField(source="department_id", read_only=True)
    department_name = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("First name cannot be blank.")
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Last name cannot be blank.")
        return value

    def validate_email(self, value):
        return value.strip().lower()

    def validate_phone_number(self, value):
        value = value.strip()
        if value and not re.fullmatch(r"[0-9+()\- ]{7,25}", value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_hire_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Hire date cannot be in the future.")
        return value
