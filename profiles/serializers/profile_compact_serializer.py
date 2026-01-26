from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from profiles.models import Profile
from profiles.services.profile_stats_service import ProfileStatsService
from uploads.services import generate_presigned_view


User = get_user_model()


class CurrentWorkSerializer(serializers.Serializer):
    """Serializer for current work experience schema"""
    job_title = serializers.CharField()
    company_name = serializers.CharField()


class ProfileCompactSerializer(serializers.Serializer):
    """
    Lightweight profile serializer for list views and embeds.
    Follows Single Responsibility - only essential fields for performance.
    """

    id = serializers.IntegerField(source='user.id')
    display_name = serializers.CharField()
    username = serializers.CharField(source='user.username')
    avatar = serializers.SerializerMethodField()
    headline = serializers.CharField(source='user.headline', allow_null=True, allow_blank=True)
    current_work = serializers.SerializerMethodField()
    is_verified = serializers.BooleanField(source='user.is_verified')
    followers_count = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        """Get avatar presigned URL"""
        if not obj.avatar:
            return None
        return generate_presigned_view(obj.avatar)

    def get_followers_count(self, obj):
        """Get followers count"""
        return ProfileStatsService.get_followers_count(obj.user)

    @extend_schema_field(CurrentWorkSerializer(allow_null=True))
    def get_current_work(self, obj):
        """Get current work experience (latest one with is_current=True or most recent)"""
        work = obj.work_experiences.filter(is_current=True).first()
        if not work:
            work = obj.work_experiences.first()  # Already ordered by -is_current, -end_year, -start_year
        if work:
            return {
                'job_title': work.job_title,
                'company_name': work.company_name,
            }
        return None


