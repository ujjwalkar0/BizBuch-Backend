from rest_framework import serializers
from posts.models import Post
from uploads.services import generate_presigned_view

class PostModelSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    author_avatar = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    imageUrl = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    def get_author_avatar(self, obj):
        if hasattr(obj.author, 'profile') and obj.author.profile and obj.author.profile.avatar:
            return generate_presigned_view(obj.author.profile.avatar)
        return None

    def get_image_url(self, obj):
        if not obj.imageUrl:
            return None
        return generate_presigned_view(obj.imageUrl)
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ["id", "created_at", "author", "author_avatar", "likes_count", "comments_count", "shares_count"]