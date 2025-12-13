from rest_framework import serializers

class TopicSelectionSerializer(serializers.Serializer):
    topic_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
