from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.models import Conversation, Message
from chat.serializers import MessageSerializer
from chat.serializers.message_serializer import MessageCreateSerializer


class MessageListView(APIView):
    """
    List messages in a conversation with pagination.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List messages in conversation",
        description="Get paginated list of messages in a conversation. Each message includes a 'type' field indicating 'sent' or 'received'.",
        parameters=[
            OpenApiParameter(
                name='page',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Page number'
            ),
            OpenApiParameter(
                name='page_size',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Number of messages per page (default: 50)'
            ),
        ],
        responses={200: MessageSerializer(many=True)},
        tags=['Chat']
    )
    def get(self, request, conversation_id):
        # Verify user is participant
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=request.user),
            id=conversation_id
        )

        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        # Get messages (newest first for pagination, then reverse for display)
        offset = (page - 1) * page_size
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by('-timestamp')[offset:offset + page_size]

        # Reverse to get chronological order
        messages = list(reversed(messages))

        serializer = MessageSerializer(messages, many=True)
        
        # Add 'type' field to each message (sent or received)
        for message_data in serializer.data:
            if message_data['sender_id'] == request.user.id:
                message_data['type'] = 'sent'
            else:
                message_data['type'] = 'received'
        
        # Get total count
        total_count = Message.objects.filter(conversation=conversation).count()
        
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'has_more': offset + page_size < total_count
        }, status=status.HTTP_200_OK)


class SendMessageView(APIView):
    """
    Send a message to another user (via REST API).
    This is an alternative to WebSocket for sending messages.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send a message",
        description="Send a message to another user. Creates conversation if it doesn't exist.",
        request=MessageCreateSerializer,
        responses={
            201: MessageSerializer,
            400: {'description': 'Bad request'},
            404: {'description': 'User not found'},
        },
        tags=['Chat']
    )
    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        serializer = MessageCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        recipient_id = serializer.validated_data['recipient_id']
        content = serializer.validated_data['content']

        if recipient_id == request.user.id:
            return Response(
                {'error': 'Cannot send message to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get or create conversation
        conversation, _ = Conversation.get_or_create_conversation(
            request.user, recipient
        )

        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )

        # Update conversation timestamp
        conversation.save()

        # Notify via WebSocket
        self._notify_websocket(message, conversation, recipient)

        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )

    def _notify_websocket(self, message, conversation, recipient):
        """Send WebSocket notifications for the new message."""
        try:
            channel_layer = get_channel_layer()
            
            # Notify the conversation room
            async_to_sync(channel_layer.group_send)(
                f'chat_{conversation.id}',
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'content': message.content,
                    'sender_id': message.sender.id,
                    'sender_username': message.sender.username,
                    'sender_first_name': message.sender.first_name,
                    'sender_last_name': message.sender.last_name,
                    'timestamp': message.timestamp.isoformat(),
                }
            )

            # Notify recipient's personal channel
            async_to_sync(channel_layer.group_send)(
                f'user_{recipient.id}_chat',
                {
                    'type': 'new_message_notification',
                    'conversation_id': conversation.id,
                    'message_id': message.id,
                    'sender_id': message.sender.id,
                    'sender_username': message.sender.username,
                    'content_preview': message.content[:100],
                    'timestamp': message.timestamp.isoformat(),
                }
            )
        except Exception:
            # WebSocket notification failed, but message was saved
            pass


class MarkMessagesReadView(APIView):
    """
    Mark messages as read.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Mark messages as read",
        description="Mark specific messages or all messages in a conversation as read",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'message_ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'description': 'List of message IDs to mark as read (optional)'
                    },
                    'mark_all': {
                        'type': 'boolean',
                        'description': 'Mark all messages in conversation as read'
                    }
                }
            }
        },
        responses={
            200: {'description': 'Messages marked as read'},
            400: {'description': 'Bad request'},
            404: {'description': 'Conversation not found'},
        },
        tags=['Chat']
    )
    def post(self, request, conversation_id):
        # Verify user is participant
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=request.user),
            id=conversation_id
        )

        message_ids = request.data.get('message_ids', [])
        mark_all = request.data.get('mark_all', False)

        # Get messages to mark as read (exclude messages sent by current user)
        messages_query = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user)

        if not mark_all and message_ids:
            messages_query = messages_query.filter(id__in=message_ids)

        # Mark as read
        updated_count = messages_query.update(
            is_read=True,
            read_at=timezone.now()
        )

        # Notify via WebSocket
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{conversation.id}',
                {
                    'type': 'messages_read',
                    'message_ids': message_ids if message_ids else list(
                        messages_query.values_list('id', flat=True)
                    ),
                    'read_by': request.user.id,
                    'read_at': timezone.now().isoformat(),
                }
            )
        except Exception:
            pass

        return Response({
            'success': True,
            'messages_marked_read': updated_count
        }, status=status.HTTP_200_OK)

