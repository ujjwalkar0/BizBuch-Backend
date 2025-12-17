from rest_framework import generics, permissions
from activity.models import Activity
from activity.serializers import ActivityLogSerializer


class ActivityLogView(generics.ListAPIView):
    """
    Activity log of the authenticated user (actor-based).
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(
            actor=self.request.user
        )
