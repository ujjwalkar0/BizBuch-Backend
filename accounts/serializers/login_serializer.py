from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from core.errors import AppError

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data["username"]
        password = data["password"]

        # Try email first, then username
        user = (
            User.objects.filter(email__iexact=identifier).first() or
            User.objects.filter(username__iexact=identifier).first()
        )

        if not user:
            raise serializers.ValidationError(AppError.INVALID_CREDENTIALS)

        user = authenticate(username=user.username, password=password)

        if not user:
            raise serializers.ValidationError(AppError.INVALID_CREDENTIALS)

        if not user.is_active:
            raise serializers.ValidationError(AppError.ACCOUNT_DISABLED)

        data["user"] = user
        return data