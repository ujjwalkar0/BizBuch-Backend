from rest_framework import serializers


class ActivityMarkReadSerializer(serializers.Serializer):
    """
    Action serializer for marking an activity as read.
    No request body is required.
    """
    pass
