from django.db import models


class ProfileWorkExperience(models.Model):
    """
    Stores multiple work experience records for a user profile.
    Allows users to list all companies and positions they've worked at.
    """
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name="work_experiences"
    )
    
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    employment_type = models.CharField(
        max_length=50,
        choices=[
            ('full-time', 'Full-time'),
            ('part-time', 'Part-time'),
            ('self-employed', 'Self-employed'),
            ('freelance', 'Freelance'),
            ('contract', 'Contract'),
            ('internship', 'Internship'),
            ('apprenticeship', 'Apprenticeship'),
            ('seasonal', 'Seasonal'),
        ],
        blank=True,
        null=True
    )
    
    start_year = models.IntegerField()
    start_month = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 13)])
    end_year = models.IntegerField(blank=True, null=True)
    end_month = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 13)])
    is_current = models.BooleanField(default=False)
    
    company_logo = models.CharField(max_length=255, blank=True, null=True)  # S3 key for company logo
    description = models.TextField(blank=True)  # Job responsibilities and achievements
    skills = models.JSONField(default=list, blank=True)  # Array of skills used in this role
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_current', '-end_year', '-start_year']
        indexes = [
            models.Index(fields=['profile', '-is_current']),
        ]
    
    def __str__(self):
        return f"{self.profile.display_name} - {self.job_title} at {self.company_name}"
