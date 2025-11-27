# users/serializers/register_serializer.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    # ---------------------------
    # Field-level validation
    # ---------------------------

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_password(self, value):
        # Uses Django’s built-in password validators
        validate_password(value)
        return value

    # ---------------------------
    # Object-level validation
    # ---------------------------

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return data

    # ---------------------------
    # Creation handled by service layer
    # ---------------------------

    def create(self, validated_data):
        """
        Not used if following SOLID. Creation is done in UserService.
        But DRF requires this for compatibility.
        """
        raise NotImplementedError(
            "Use UserService.create_user(data) instead of serializer.create()"
        )
