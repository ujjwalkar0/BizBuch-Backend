from activity.services import NotificationService
from intelligence.services import PostRecommendationService
from posts.models import PostComment, Post
from django.db import transaction

class CommentService:

    @staticmethod
    def list_comments(post_id):
        return PostComment.objects.filter(post_id=post_id).order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def create_comment(user, post_id, validated_data):
        post = Post.objects.get(id=post_id)

        comment = PostComment.objects.create(
            user=user,
            post=post,
            content=validated_data["content"]
        )

        PostRecommendationService.on_comment_added(comment)
        NotificationService.on_comment_added(comment=comment)

        return comment

    @staticmethod
    def update_comment(comment, validated_data):
        comment.content = validated_data.get("content", comment.content)
        comment.save()
        return comment

    @staticmethod
    def delete_comment(comment):
        comment.delete()
