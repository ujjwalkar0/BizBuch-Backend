from rest_framework import serializers


class ActivityMarkAllReadSerializer(serializers.Serializer):
    """
    Action serializer for marking an activity as read.
    No request body is required.
    """
    pass
