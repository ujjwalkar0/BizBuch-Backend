from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from profiles.services import ConnectionsService
from profiles.serializers import ProfileCompactSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Connections"])
class ConnectionsAPIView(ListAPIView):
    """
    Get the authenticated user's connections (followers + following).
    
    Returns a list of profiles that the user is connected with.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileCompactSerializer

    def get_queryset(self):
        return ConnectionsService.get_connections(self.request.user)

