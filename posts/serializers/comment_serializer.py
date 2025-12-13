from rest_framework import serializers
from posts.models.post_comment import PostComment

class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = PostComment
        fields = ["id", "post", "user", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at", "post"]
