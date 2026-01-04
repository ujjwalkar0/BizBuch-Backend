from posts.models import Post
from django.db.models import F, Case, When, IntegerField

class PostService:

    @staticmethod
    def create_post(user, validated_data):
        print(validated_data)
        return Post.objects.create(user=user, **validated_data)

    @staticmethod
    def update_post(post, validated_data):
        for field, value in validated_data.items():
            setattr(post, field, value)
        post.save()
        return post

    @staticmethod
    def delete_post(post):
        post.delete()
        return True

    @staticmethod
    def increase_like_count(post):
        Post.objects.filter(id=post.id).update(
            likes_count=F("likes_count") + 1
        )

    """
    Think about this solution for future
    from django.db.models import F, Func, IntegerField

    class Greatest(Func):
        function = "GREATEST"
        output_field = IntegerField()
    ...
    Post.objects.filter(id=post.id).update(
        likes_count=Greatest(F("likes_count") - 1, 0)
    )
    """

    @staticmethod
    def decrease_like_count(post):
        Post.objects.filter(id=post.id).update(
            likes_count=Case(
                When(likes_count__gt=0, then=F("likes_count") - 1),
                default=0,
                output_field=IntegerField(),
            )
        )
