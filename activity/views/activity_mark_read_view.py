from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from activity.models import Activity
from activity.services import ActivityService
from activity.serializers import ActivityMarkReadSerializer


class ActivityMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivityMarkReadSerializer

    def post(self, request, pk):
        activity = Activity.objects.get(
            pk=pk,
            recipient=request.user
        )
        ActivityService.mark_as_read(activity)
        return Response(status=status.HTTP_204_NO_CONTENT)