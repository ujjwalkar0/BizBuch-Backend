from rest_framework import serializers

class PresignUploadRequestSerializer(serializers.Serializer):
    contentType = serializers.CharField(max_length=100)
    fileName = serializers.CharField(max_length=255)

    def validate_contentType(self, value):
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp",
        ]

        if value not in allowed_types:
            raise serializers.ValidationError(
                "Unsupported file type"
            )

        return value