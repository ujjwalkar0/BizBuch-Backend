from django.db import models


class ProfileEducation(models.Model):
    """
    Stores multiple education records for a user profile.
    Allows users to list all schools and universities they attended.
    """
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name="educations"
    )
    
    name = models.CharField(max_length=255)  # School/University name
    degrees = models.JSONField(default=list, blank=True)  # Array of degrees e.g., ["Bachelor of Science", "Master of Engineering"]
    duration = models.CharField(max_length=100, blank=True, null=True)  # e.g., "2015-2019" or "2015-Present"
    start_year = models.IntegerField(blank=True, null=True)
    end_year = models.IntegerField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    school_logo = models.CharField(max_length=255, blank=True, null=True)  # S3 key for school logo
    description = models.TextField(blank=True)  # Additional details about education
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_current', '-end_year', '-start_year']
        indexes = [
            models.Index(fields=['profile', '-is_current']),
        ]
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.name}"
