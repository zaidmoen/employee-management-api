import re

from rest_framework import serializers


class EmergencyContactSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    relationship = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=25)
    email = serializers.EmailField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

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
