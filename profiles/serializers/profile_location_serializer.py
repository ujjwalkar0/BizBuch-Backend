from rest_framework import serializers
from profiles.models import ProfileLocation, ProfileEducation, ProfileWorkExperience
from uploads.services import generate_presigned_view


class ProfileLocationSerializer(serializers.ModelSerializer):
    """Serializer for user profile locations"""
    
    class Meta:
        model = ProfileLocation
        fields = [
            'id',
            'location',
            'is_primary',
            'location_type',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProfileEducationSerializer(serializers.ModelSerializer):
    """Serializer for user profile education"""
    
    school_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfileEducation
        fields = [
            'id',
            'name',
            'degrees',
            'duration',
            'start_year',
            'end_year',
            'is_current',
            'school_logo',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_school_logo(self, obj):
        """Get school logo presigned URL"""
        if not obj.school_logo:
            return None
        return generate_presigned_view(obj.school_logo)


class ProfileWorkExperienceSerializer(serializers.ModelSerializer):
    """Serializer for user profile work experience"""
    
    company_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfileWorkExperience
        fields = [
            'id',
            'company_name',
            'job_title',
            'location',
            'employment_type',
            'start_year',
            'start_month',
            'end_year',
            'end_month',
            'is_current',
            'company_logo',
            'description',
            'skills',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_company_logo(self, obj):
        """Get company logo presigned URL"""
        if not obj.company_logo:
            return None
        return generate_presigned_view(obj.company_logo)

