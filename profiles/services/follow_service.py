from profiles.models import ProfileFollow
from django.core.exceptions import ValidationError
from activity.services import NotificationService

class FollowService:

    @staticmethod
    def follow(user, target_user):
        if user == target_user:
            raise ValidationError("You cannot follow yourself.")

        follow = ProfileFollow.objects.get_or_create(
            follower=user,
            following=target_user
        )

        NotificationService.on_user_followed(follow)

    @staticmethod
    def unfollow(user, target_user):
        ProfileFollow.objects.filter(
            follower=user,
            following=target_user
        ).delete()
