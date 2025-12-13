from rest_framework import serializers

class OnboardingStatusSerializer(serializers.Serializer):
    completed = serializers.BooleanField()
