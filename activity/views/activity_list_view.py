from rest_framework import generics, permissions, status
from rest_framework.response import Response

from activity.models import Activity
from activity.serializers import ActivitySerializer
from activity.services import ActivityService


class ActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(
            recipient=self.request.user
        )


