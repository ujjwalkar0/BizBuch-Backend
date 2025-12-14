from profiles.models import ProfileFollow
from django.core.exceptions import ValidationError


class FollowService:

    @staticmethod
    def follow(user, target_user):
        if user == target_user:
            raise ValidationError("You cannot follow yourself.")

        ProfileFollow.objects.get_or_create(
            follower=user,
            following=target_user
        )

    @staticmethod
    def unfollow(user, target_user):
        ProfileFollow.objects.filter(
            follower=user,
            following=target_user
        ).delete()
