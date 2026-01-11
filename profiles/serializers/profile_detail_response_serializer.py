from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile
from profiles.services.profile_stats_service import ProfileStatsService
from profiles.serializers.profile_location_serializer import (
    ProfileLocationSerializer,
    ProfileEducationSerializer,
    ProfileWorkExperienceSerializer
)
from uploads.services import generate_presigned_view


User = get_user_model()


class ProfileDetailResponseSerializer(serializers.Serializer):
    """
    Detailed profile response serializer with all fields.
    Follows Single Responsibility Principle - aggregates data from Profile and User models.
    Follows Open/Closed Principle - can be extended without modifying.
    """

    # Basic Info
    id = serializers.IntegerField(source='user.id')
    display_name = serializers.CharField()
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True)
    avatar = serializers.SerializerMethodField()

    # Professional Info
    headline = serializers.CharField(source='user.headline', allow_null=True, allow_blank=True)
    current_position = serializers.CharField(source='user.current_position', allow_null=True, allow_blank=True)
    company = serializers.CharField(source='user.company', allow_null=True, allow_blank=True)
    company_logo = serializers.SerializerMethodField()
    industry = serializers.CharField(source='user.industry', allow_null=True, allow_blank=True)
    
    # Locations (multiple)
    locations = ProfileLocationSerializer(many=True, read_only=True)

    # Contact & Links
    email = serializers.SerializerMethodField()
    phone = serializers.CharField(source='user.phone', allow_null=True, allow_blank=True)
    website = serializers.URLField(source='user.website', allow_null=True, allow_blank=True)
    linkedin_url = serializers.URLField(source='user.linkedin_url', allow_null=True, allow_blank=True)
    twitter_url = serializers.URLField(source='user.twitter_url', allow_null=True, allow_blank=True)

    # Stats
    connections_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    # Connection Status (for viewing other users)
    is_connected = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    mutual_connections_count = serializers.SerializerMethodField()

    # Verification & Status
    is_verified = serializers.BooleanField(source='user.is_verified')
    is_premium = serializers.BooleanField(source='user.is_premium')
    account_type = serializers.CharField(source='user.account_type')

    # Additional
    cover_image = serializers.SerializerMethodField()
    joined_date = serializers.DateTimeField(source='user.joined_date')
    skills = serializers.ListField(child=serializers.CharField())
    
    # Education (multiple)
    educations = ProfileEducationSerializer(many=True, read_only=True)
    
    # Work Experience (multiple)
    work_experiences = ProfileWorkExperienceSerializer(many=True, read_only=True)
    
    open_to_work = serializers.BooleanField(source='user.open_to_work')
    open_to_hire = serializers.BooleanField(source='user.open_to_hire')

    def __init__(self, *args, **kwargs):
        """Store viewing user in context for connection status"""
        super().__init__(*args, **kwargs)
        self.viewing_user = None
        if hasattr(self, 'context') and 'request' in self.context:
            if self.context['request'].user.is_authenticated:
                self.viewing_user = self.context['request'].user

    def get_avatar(self, obj):
        """Get avatar presigned URL"""
        if not obj.avatar:
            return None
        return generate_presigned_view(obj.avatar)

    def get_company_logo(self, obj):
        """Get company logo presigned URL"""
        if not obj.company_logo:
            return None
        return generate_presigned_view(obj.company_logo)

    def get_cover_image(self, obj):
        """Get cover image presigned URL"""
        if not obj.cover_image:
            return None
        return generate_presigned_view(obj.cover_image)

    def get_email(self, obj):
        """Get email (only if viewing own profile or user is staff)"""
        viewing_user = self.viewing_user
        if viewing_user and (viewing_user == obj.user or viewing_user.is_staff):
            return obj.user.email
        return None

    def get_connections_count(self, obj):
        """Get connections count from service"""
        return ProfileStatsService.get_connections_count(obj.user)

    def get_followers_count(self, obj):
        """Get followers count from service"""
        return ProfileStatsService.get_followers_count(obj.user)

    def get_following_count(self, obj):
        """Get following count from service"""
        return ProfileStatsService.get_following_count(obj.user)

    def get_posts_count(self, obj):
        """Get posts count from service"""
        return ProfileStatsService.get_posts_count(obj.user)

    def get_is_connected(self, obj):
        """Check if viewing user is connected"""
        if self.viewing_user and self.viewing_user != obj.user:
            return ProfileStatsService.is_connected(self.viewing_user, obj.user)
        return False

    def get_is_following(self, obj):
        """Check if viewing user is following"""
        if self.viewing_user and self.viewing_user != obj.user:
            return ProfileStatsService.is_following(self.viewing_user, obj.user)
        return False

    def get_mutual_connections_count(self, obj):
        """Get mutual connections count"""
        if self.viewing_user and self.viewing_user != obj.user:
            return ProfileStatsService.get_mutual_connections_count(self.viewing_user, obj.user)
        return 0


