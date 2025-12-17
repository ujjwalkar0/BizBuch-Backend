from rest_framework import generics, permissions, status
from rest_framework.response import Response
from activity.services import ActivityService
from activity.serializers import ActivityMarkAllReadSerializer

class ActivityMarkAllReadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivityMarkAllReadSerializer

    def post(self, request):
        ActivityService.mark_all_as_read(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
