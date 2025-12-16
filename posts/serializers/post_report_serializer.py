from rest_framework import serializers
from posts.models import PostReport


class PostReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.ReadOnlyField(source="reported_by.username")

    class Meta:
        model = PostReport
        fields = ["id", "reported_by", "post", "reason", "created_at"]
        read_only_fields = ["id", "reported_by", "post", "created_at"]
