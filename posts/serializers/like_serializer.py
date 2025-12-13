from rest_framework import serializers
from posts.models.post_like import PostLike

class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = PostLike
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["id", "user", "post", "created_at"]
