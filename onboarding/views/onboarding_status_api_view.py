from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from onboarding.serializers import OnboardingStatusSerializer


class OnboardingStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OnboardingStatusSerializer

    def get(self, request):
        return Response({
            "completed": request.user.has_completed_onboarding
        })
