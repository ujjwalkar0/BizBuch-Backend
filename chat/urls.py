from django.urls import path
from chat.views import (
    ConversationListView,
    ConversationDetailView,
    StartConversationView,
    MessageListView,
    SendMessageView,
    MarkMessagesReadView,
)

urlpatterns = [
    # Conversation endpoints
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/start/', StartConversationView.as_view(), name='conversation-start'),
    
    # Message endpoints
    path('conversations/<int:conversation_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('conversations/<int:conversation_id>/read/', MarkMessagesReadView.as_view(), name='mark-read'),
    path('send/', SendMessageView.as_view(), name='send-message'),
]
