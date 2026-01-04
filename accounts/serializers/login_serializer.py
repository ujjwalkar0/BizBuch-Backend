from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data["username"]
        password = data["password"]

        # Try email first
        user = User.objects.filter(email__iexact=identifier).first()

        print("User found by email:", user)

        # If not email, try username
        if not user:
            user = User.objects.filter(username__iexact=identifier).first()

            print("User found by username:", user)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        user = authenticate(
            username=user.username,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account disabled")

        data["user"] = user
        return data
