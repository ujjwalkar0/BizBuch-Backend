from typing import Optional
from rest_framework import serializers
from activity.models import Activity


class ActivityLogSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "verb",
            "target_type",
            "target_id",
            "created_at",
        ]

    def get_target_type(self, obj: Activity) -> Optional[str]:
        return obj.target_content_type.model if obj.target_content_type else None

    def get_target_id(self, obj: Activity) -> Optional[int]:
        return obj.target_object_id
