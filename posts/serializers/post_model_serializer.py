from rest_framework import serializers
from posts.models import Post
from uploads.services import generate_presigned_view

class PostModelSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if not obj.imageUrl:
            return None
        return generate_presigned_view(obj.imageUrl)
    
    class Meta:
        model = Post
        # fields = '__all__'
        exclude = ['imageUrl']
        read_only_fields = ["id", "created_at", "author", "likes_count", "comments_count", "shares_count"]