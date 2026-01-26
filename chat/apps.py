from django.apps import AppConfig
import os


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    path = os.path.dirname(os.path.abspath(__file__))
