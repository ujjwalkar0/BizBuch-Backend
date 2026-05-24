from uploads.services.generate_presigned_view import generate_presigned_view
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_photo",
        ]

    def get_profile_photo(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return generate_presigned_view(obj.profile.avatar)
        return None