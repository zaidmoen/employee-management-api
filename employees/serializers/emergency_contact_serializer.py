import re

from rest_framework import serializers

from employees.models import EmergencyContact


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "name",
            "relationship",
            "phone_number",
            "email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Contact name cannot be blank.")
        return value

    def validate_relationship(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Relationship cannot be blank.")
        return value

    def validate_phone_number(self, value):
        value = value.strip()
        if not re.fullmatch(r"[0-9+()\- ]{7,25}", value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_email(self, value):
        return value.strip().lower()
