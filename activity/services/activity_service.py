from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from activity.models import Activity, ActivityPreference


class ActivityService:
    @staticmethod
    def create_activity(*, actor, recipient, verb, target=None):
        """
        Central place to create activities.
        """

        if actor == recipient:
            return None  # no self notifications

        # Check user preferences
        preference = getattr(recipient, "activity_preferences", None)

        if preference:
            if verb == "liked" and not preference.notify_like:
                return None
            if verb == "commented" and not preference.notify_comment:
                return None
            if verb == "followed" and not preference.notify_follow:
                return None

        target_content_type = None
        target_object_id = None

        if target:
            target_content_type = ContentType.objects.get_for_model(target)
            target_object_id = target.id

        return Activity.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            target_content_type=target_content_type,
            target_object_id=target_object_id,
        )

    @staticmethod
    def mark_as_read(activity: Activity):
        if not activity.is_read:
            activity.is_read = True
            activity.read_at = timezone.now()
            activity.save(update_fields=["is_read", "read_at"])

    @staticmethod
    def mark_all_as_read(user):
        Activity.objects.filter(
            recipient=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
    @staticmethod
    def on_comment_added(*, comment):
        """
        Triggered when a new comment is added to a post.
        Creates an activity for the post owner.
        """

        post = comment.post
        actor = comment.user
        recipient = post.user

        ActivityService.create_activity(
            actor=actor,
            recipient=recipient,
            verb="commented",
            target=comment,
        )
