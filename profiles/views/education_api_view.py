from rest_framework import generics, permissions
from profiles.models import ProfileEducation
from profiles.serializers import ProfileEducationSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Education"])
class EducationCreateAPIView(generics.CreateAPIView):
    """
    Create a new education entry.
    """
    serializer_class = ProfileEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

@extend_schema(tags=["Education"])
class EducationUpdateDeleteAPIView(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update (PATCH) or delete a specific education entry.
    """
    serializer_class = ProfileEducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "delete"]

    def get_queryset(self):
        return ProfileEducation.objects.filter(profile=self.request.user.profile)
