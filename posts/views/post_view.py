from rest_framework import generics, permissions
from posts.models import Post
from posts.serializers import PostModelSerializer
from posts.permissions import IsOwner
from posts.services import PostService

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        PostService.create_post(self.request.user, serializer.validated_data)


class PostRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostModelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_update(self, serializer):
        PostService.update_post(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        PostService.delete_post(instance)


# Following Scenario need to Test:
# - Create a Post from User A
# - Retrieve the from User B
# - Check will if it works fine or not?