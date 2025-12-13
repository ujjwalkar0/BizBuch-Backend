from django.db import transaction
from onboarding.models import UserTopic
from intelligence.services import PostRecommendationService

class OnboardingService:

    @staticmethod
    @transaction.atomic
    def submit_topics(*, user, topic_ids):
        """
        Replace user's selected topics and mark onboarding as completed.
        """

        UserTopic.objects.filter(user=user).delete()

        UserTopic.objects.bulk_create([
            UserTopic(user=user, topic_id=topic_id)
            for topic_id in topic_ids
        ])

        user.has_completed_onboarding = True
        user.save(update_fields=["has_completed_onboarding"])

        PostRecommendationService.on_successfull_onboarding(user, topic_ids)