from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket URL for specific conversation
    re_path(
        r'ws/chat/(?P<conversation_id>\d+)/$',
        consumers.ChatConsumer.as_asgi()
    ),
    # WebSocket URL for user-level notifications
    re_path(
        r'ws/chat/notifications/$',
        consumers.UserChatConsumer.as_asgi()
    ),
]
