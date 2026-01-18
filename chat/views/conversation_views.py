from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter

from chat.models import Conversation
from chat.serializers import ConversationSerializer, ConversationListSerializer


class ConversationListView(APIView):
    """
    List all conversations for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List user's conversations",
        description="Get all conversations for the authenticated user with preview of last message",
        responses={200: ConversationListSerializer(many=True)},
        tags=['Chat']
    )
    def get(self, request):
        conversations = Conversation.objects.filter(
            participants=request.user
        ).prefetch_related('participants', 'messages').distinct()

        serializer = ConversationListSerializer(
            conversations,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ConversationDetailView(APIView):
    """
    Get details of a specific conversation including all messages.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get conversation details",
        description="Get detailed view of a conversation with all messages",
        responses={200: ConversationSerializer},
        tags=['Chat']
    )
    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=request.user),
            id=conversation_id
        )

        serializer = ConversationSerializer(
            conversation,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class StartConversationView(APIView):
    """
    Start a new conversation with another user or get existing one.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Start or get conversation",
        description="Start a new conversation with a user or get the existing one",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user_id': {
                        'type': 'integer',
                        'description': 'ID of the user to start conversation with'
                    }
                },
                'required': ['user_id']
            }
        },
        responses={
            200: ConversationSerializer,
            201: ConversationSerializer,
            400: {'description': 'Bad request'},
            404: {'description': 'User not found'},
        },
        tags=['Chat']
    )
    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if int(user_id) == request.user.id:
            return Response(
                {'error': 'Cannot start conversation with yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        conversation, created = Conversation.get_or_create_conversation(
            request.user, other_user
        )

        serializer = ConversationSerializer(
            conversation,
            context={'request': request}
        )

        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)
