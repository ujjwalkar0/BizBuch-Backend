from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from rest_framework.filters import SearchFilter

class ProfileListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.filter(is_public=True).select_related("user")

    filter_backends = [SearchFilter]
    search_fields = ["display_name"]

#  class ProfileListAPIView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ProfileSerializer

#     def get_queryset(self):
#         qs = Profile.objects.filter(is_public=True)

#         search = self.request.query_params.get("search")
#         if search:
#             qs = qs.filter(display_name__icontains=search)

#         return qs.select_related("user")
