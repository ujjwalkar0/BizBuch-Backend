from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile
from profiles.services.profile_stats_service import ProfileStatsService
from uploads.services import generate_presigned_view


User = get_user_model()


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
    company = serializers.CharField(source='user.company', allow_null=True, allow_blank=True)
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


