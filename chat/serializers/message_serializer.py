from rest_framework import serializers
from chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_first_name = serializers.CharField(source='sender.first_name', read_only=True)
    sender_last_name = serializers.CharField(source='sender.last_name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender_id',
            'sender_username',
            'sender_first_name',
            'sender_last_name',
            'content',
            'timestamp',
            'is_read',
            'read_at',
        ]
        read_only_fields = ['id', 'timestamp', 'is_read', 'read_at']


class MessageCreateSerializer(serializers.Serializer):
    """Serializer for creating a new message."""
    recipient_id = serializers.IntegerField()
    content = serializers.CharField(max_length=5000)

    def validate_recipient_id(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User does not exist.")
        
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value.strip()
