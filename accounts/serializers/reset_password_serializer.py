from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def validate_new_password(self, value):
        validate_password(value)  # Django's built-in strength validator
        return value
