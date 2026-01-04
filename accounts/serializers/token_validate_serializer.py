from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenValidateSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, attrs):
        token = attrs.get("token")
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)
        except Exception:
            raise serializers.ValidationError("Invalid or expired token")

        if not user.is_active:
            raise serializers.ValidationError("User account disabled")

        attrs["user"] = user
        return attrs
