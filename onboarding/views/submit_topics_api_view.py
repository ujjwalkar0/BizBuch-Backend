from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from onboarding.serializers import TopicSelectionSerializer
from onboarding.services import OnboardingService


class SubmitTopicsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TopicSelectionSerializer

    def post(self, request):
        serializer = TopicSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        OnboardingService.submit_topics(
            user=request.user,
            topic_ids=serializer.validated_data["topic_ids"]
        )

        return Response({"message": "Onboarding completed"})
