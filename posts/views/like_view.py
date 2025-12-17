from rest_framework import generics, permissions, status
from rest_framework.response import Response
from posts.serializers.like_serializer import PostLikeSerializer
from posts.models import PostLike
from posts.permissions import IsOwner
from posts.services import LikeService
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Likes"])
class PostLikeListCreateView(generics.ListCreateAPIView):
    serializer_class = PostLikeSerializer

    # Anyone can see likes
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LikeService.list_likes(self.kwargs["post_id"])

    def perform_create(self, serializer):
        LikeService.like_post(
            user=self.request.user,
            post_id=self.kwargs["post_id"]
        )


@extend_schema(tags=["Likes"])
class PostLikeDeleteView(generics.DestroyAPIView):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_destroy(self, instance):
        LikeService.delete_like(instance)
