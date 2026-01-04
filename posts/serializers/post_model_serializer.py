from rest_framework import serializers
from posts.models import Post

class PostModelSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ["id", "created_at", "author", "likes_count", "comments_count", "shares_count"]