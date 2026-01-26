from django.db import models, transaction
from django.conf import settings


class Conversation(models.Model):
    """
    Represents a conversation between two users.
    A conversation is unique between any two users.
    """
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = ', '.join([user.username for user in self.participants.all()])
        return f"Conversation: {participant_names}"

    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        return self.participants.exclude(id=user.id).first()

    def get_last_message(self):
        """Get the most recent message in the conversation."""
        return self.messages.order_by('-timestamp').first()

    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        """
        Get an existing conversation between two users or create a new one.
        Uses select_for_update to prevent race conditions.
        """
        with transaction.atomic():
            # Lock and find conversations where both users are participants
            conversation = cls.objects.select_for_update().filter(
                participants=user1
            ).filter(participants=user2).first()
            
            if conversation:
                return conversation, False
            
            # Create new conversation
            conversation = cls.objects.create()
            conversation.participants.add(user1, user2)
            return conversation, True
