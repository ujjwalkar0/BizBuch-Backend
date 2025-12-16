from rest_framework import serializers
from activity.models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "actor_username",
            "verb",
            "is_read",
            "created_at",
        ]
