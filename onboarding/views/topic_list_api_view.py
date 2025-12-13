from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from onboarding.models import Topic
from onboarding.serializers import TopicSerializer

class TopicListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSerializer

    def get(self, request):
        topics = Topic.objects.filter(is_active=True)
        return Response(TopicSerializer(topics, many=True).data)
