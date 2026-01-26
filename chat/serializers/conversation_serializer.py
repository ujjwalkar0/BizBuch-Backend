from rest_framework import serializers
from chat.models import Conversation, Message
from chat.serializers.message_serializer import MessageSerializer
from uploads.services import generate_presigned_view


class ConversationParticipantSerializer(serializers.Serializer):
    """Serializer for conversation participants."""
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    headline = serializers.CharField(allow_null=True)
    avatar = serializers.CharField(allow_null=True)


class ConversationSerializer(serializers.ModelSerializer):
    """Detailed serializer for a single conversation."""
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'participants',
            'messages',
            'created_at',
            'updated_at',
        ]


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations with preview."""
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'other_participant',
            'last_message',
            'unread_count',
            'created_at',
            'updated_at',
        ]

    def get_other_participant(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other_user = obj.get_other_participant(request.user)
            if other_user:
                avatar_url = None
                if hasattr(other_user, 'profile') and other_user.profile and other_user.profile.avatar:
                    avatar_url = generate_presigned_view(other_user.profile.avatar)
                return {
                    'id': other_user.id,
                    'username': other_user.username,
                    'first_name': other_user.first_name,
                    'last_name': other_user.last_name,
                    'headline': getattr(other_user, 'headline', None),
                    'avatar': avatar_url,
                }
        return None

    def get_last_message(self, obj):
        last_message = obj.get_last_message()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content[:100],  # Preview
                'sender_id': last_message.sender.id,
                'timestamp': last_message.timestamp,
                'is_read': last_message.is_read,
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
