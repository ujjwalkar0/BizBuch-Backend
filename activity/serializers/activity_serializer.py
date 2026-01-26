from rest_framework import serializers
from activity.models import Activity
from uploads.services import generate_presigned_view


class ActivitySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)
    actor_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "actor_username",
            "actor_avatar_url",
            "verb",
            "is_read",
            "created_at",
        ]

    def get_actor_avatar_url(self, obj):
        """Get actor's avatar presigned URL"""
        if hasattr(obj.actor, 'profile') and obj.actor.profile and obj.actor.profile.avatar:
            return generate_presigned_view(obj.actor.profile.avatar)
        return None
