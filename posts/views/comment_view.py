from rest_framework import generics, permissions
from posts.models import PostComment
from posts.serializers import PostCommentSerializer
from posts.permissions import IsOwner
from posts.services import CommentService
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Comments"])
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommentService.list_comments(self.kwargs["post_id"])

    def perform_create(self, serializer):
        CommentService.create_comment(
            user=self.request.user,
            post_id=self.kwargs["post_id"],
            validated_data=serializer.validated_data
        )


@extend_schema(tags=["Comments"])
class CommentRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_update(self, serializer):
        CommentService.update_comment(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        CommentService.delete_comment(instance)
