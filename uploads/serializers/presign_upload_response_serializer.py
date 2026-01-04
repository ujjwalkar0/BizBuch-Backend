from rest_framework import serializers

class PresignUploadResponseSerializer(serializers.Serializer):
    uploadUrl = serializers.URLField()
    publicUrl = serializers.URLField()