from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile, ProfileLocation
from profiles.serializers.profile_location_serializer import ProfileLocationSerializer


User = get_user_model()


class ProfileUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating profile and user information.
    Separates read and write operations - follows Single Responsibility Principle.
    """

    # Basic Info
    display_name = serializers.CharField(max_length=150, required=False)
    bio = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.CharField(required=False, allow_null=True)

    # Professional Info (User model)
    headline = serializers.CharField(max_length=255, required=False, allow_blank=True)
    current_position = serializers.CharField(max_length=255, required=False, allow_blank=True)
    company = serializers.CharField(max_length=255, required=False, allow_blank=True)
    industry = serializers.CharField(max_length=100, required=False, allow_blank=True)

    # Professional Info (Profile model)
    company_logo = serializers.CharField(required=False, allow_null=True)
    cover_image = serializers.CharField(required=False, allow_null=True)

    # Contact & Links
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)
    twitter_url = serializers.URLField(required=False, allow_blank=True)

    # Status
    account_type = serializers.ChoiceField(
        choices=['personal', 'business', 'creator'],
        required=False
    )
    open_to_work = serializers.BooleanField(required=False)
    open_to_hire = serializers.BooleanField(required=False)

    # Privacy
    is_public = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        """
        Update both User and Profile models, including related models.
        
        Args:
            instance: Profile instance
            validated_data: Validated data from request
        
        Returns:
            Updated Profile instance
        """
        # instance is Profile, not User
        profile = instance
        user = instance.user
        
        # Update Profile model fields
        profile_fields = [
            'display_name', 'bio', 'avatar',
            'company_logo', 'cover_image', 'is_public'
        ]
        
        for field in profile_fields:
            if field in validated_data:
                setattr(profile, field, validated_data.pop(field))
        
        profile.save()
        
        # Update User model fields
        user_fields = [
            'headline', 'current_position', 'company', 'industry',
            'phone', 'website', 'linkedin_url', 'twitter_url',
            'account_type', 'open_to_work', 'open_to_hire'
        ]
        
        for field in user_fields:
            if field in validated_data:
                setattr(user, field, validated_data.pop(field))
        
        user.save()
        
        return instance



