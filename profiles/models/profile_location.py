from django.db import models


class ProfileLocation(models.Model):
    """
    Stores multiple locations for a user profile.
    Allows users to have current, previous, or multiple work locations.
    """
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name="locations"
    )
    
    location = models.CharField(max_length=255)  # e.g., "San Francisco, CA"
    is_primary = models.BooleanField(default=False)  # Current location
    location_type = models.CharField(
        max_length=20,
        choices=[
            ('current', 'Current'),
            ('previous', 'Previous'),
            ('hometown', 'Hometown'),
            ('other', 'Other'),
        ],
        default='other'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['profile', '-is_primary']),
        ]
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.location}"
