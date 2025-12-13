from rest_framework import serializers
from posts.models import Post

class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Post
        fields = ["id", "user", "content", "image", "created_at"]
        read_only_fields = ["id", "created_at", "user"]