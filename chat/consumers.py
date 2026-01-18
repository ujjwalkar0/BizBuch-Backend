import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality.
    Handles:
    - Sending/receiving messages
    - Typing indicators
    - Read receipts
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope['user']
        
        # Reject anonymous users
        if self.user.is_anonymous:
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required. Please provide a valid token.'
            }))
            await self.close(code=4001)
            return

        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Verify user is a participant in this conversation
        is_participant = await self.is_user_participant()
        if not is_participant:
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'error',
                'code': 'FORBIDDEN',
                'message': 'You are not a participant in this conversation.'
            }))
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify others that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_online',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            # Notify others that user is offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_offline',
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'stop_typing':
                await self.handle_stop_typing(data)
            elif message_type == 'mark_read':
                await self.handle_mark_read(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def handle_chat_message(self, data):
        """Handle sending a new chat message."""
        content = data.get('content', '').strip()
        
        if not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return

        # Save message to database
        message = await self.save_message(content)

        # Broadcast message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message_id': message.id,
                'content': message.content,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'sender_first_name': self.user.first_name,
                'sender_last_name': self.user.last_name,
                'timestamp': message.timestamp.isoformat(),
            }
        )

    async def handle_typing(self, data):
        """Handle typing indicator."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': True,
            }
        )

    async def handle_stop_typing(self, data):
        """Handle stop typing indicator."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': False,
            }
        )

    async def handle_mark_read(self, data):
        """Handle marking messages as read."""
        message_ids = data.get('message_ids', [])
        
        if message_ids:
            await self.mark_messages_read(message_ids)
            
            # Notify sender that messages were read
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'message_ids': message_ids,
                    'read_by': self.user.id,
                    'read_at': timezone.now().isoformat(),
                }
            )

    # Event handlers for group messages
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'content': event['content'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_first_name': event['sender_first_name'],
            'sender_last_name': event['sender_last_name'],
            'timestamp': event['timestamp'],
        }))

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def messages_read(self, event):
        """Send read receipt to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'message_ids': event['message_ids'],
            'read_by': event['read_by'],
            'read_at': event['read_at'],
        }))

    async def user_online(self, event):
        """Send user online notification."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_online',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    async def user_offline(self, event):
        """Send user offline notification."""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_offline',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    # Database operations
    @database_sync_to_async
    def is_user_participant(self):
        """Check if the current user is a participant in the conversation."""
        from chat.models import Conversation
        return Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.user
        ).exists()

    @database_sync_to_async
    def save_message(self, content):
        """Save a message to the database."""
        from chat.models import Message, Conversation
        
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )
        
        # Update conversation's updated_at timestamp
        conversation.save()
        
        return message

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read."""
        from chat.models import Message
        
        Message.objects.filter(
            id__in=message_ids,
            conversation_id=self.conversation_id
        ).exclude(
            sender=self.user
        ).update(
            is_read=True,
            read_at=timezone.now()
        )


class UserChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for user-level chat notifications.
    Allows users to receive notifications about new messages across all conversations.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return

        self.user_group_name = f'user_{self.user.id}_chat'

        # Join user's personal notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming messages."""
        pass  # This consumer is primarily for receiving notifications

    async def new_message_notification(self, event):
        """Send new message notification to user."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': event['conversation_id'],
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'content_preview': event['content_preview'],
            'timestamp': event['timestamp'],
        }))
