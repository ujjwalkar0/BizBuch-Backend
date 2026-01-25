from rest_framework import generics, permissions
from profiles.models import ProfileWorkExperience
from profiles.serializers import ProfileWorkExperienceSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Work Experience"])
class WorkExperienceCreateAPIView(generics.CreateAPIView):
    """
    Create a new work experience entry.
    """
    serializer_class = ProfileWorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

@extend_schema(tags=["Work Experience"])
class WorkExperienceUpdateDeleteAPIView(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update (PATCH) or delete a specific work experience entry.
    """
    serializer_class = ProfileWorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "delete"]

    def get_queryset(self):
        return ProfileWorkExperience.objects.filter(profile=self.request.user.profile)
