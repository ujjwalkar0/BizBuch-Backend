from rest_framework import serializers
from profiles.models import Profile

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "display_name",
            "bio",
            "avatar",
            "is_public",
        ]
