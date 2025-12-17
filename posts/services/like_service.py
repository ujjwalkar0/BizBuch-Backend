from django.db import IntegrityError
from posts.models import PostLike, Post
from posts.services import PostService
from django.db import transaction, IntegrityError
from intelligence.services import PostRecommendationService
from activity.services import NotificationService

class LikeService:

    @staticmethod
    def list_likes(post_id):
        return PostLike.objects.filter(post_id=post_id).order_by("-created_at")

    @staticmethod
    def like_post(user, post_id):
        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)

            try:
                like = PostLike.objects.create(user=user, post=post)
            except IntegrityError:
                return False
                
            PostService.increase_like_count(post)
            PostRecommendationService.on_new_like(post)
            NotificationService.on_post_liked(like)
            
            
        
        return True

    @staticmethod
    def delete_like(like_instance):
        like_instance.delete()
