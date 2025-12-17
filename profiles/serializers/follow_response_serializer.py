from rest_framework import serializers

class FollowResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
