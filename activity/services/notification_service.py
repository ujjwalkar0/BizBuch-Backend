from activity.services.activity_service import ActivityService
from posts.models import PostLike, PostComment
from profiles.models import ProfileFollow


class NotificationService:
    @staticmethod
    def on_comment_added(*, comment: PostComment):
        post = comment.post

        ActivityService.create_activity(
            actor=comment.user,
            recipient=post.user,
            verb="commented",
            target=comment,
        )

    @staticmethod
    def on_post_liked(*, like: PostLike):
        ActivityService.create_activity(
            actor=like.user,
            recipient=like.post.user,
            verb="liked",
            target=like.post,
        )

    @staticmethod
    def on_user_followed(*, follow: ProfileFollow):
        ActivityService.create_activity(
            actor=follow.follower,
            recipient=follow.following,
            verb="followed",
            target=follow.following,
        )
