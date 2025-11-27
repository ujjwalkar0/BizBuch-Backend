from django.db import models
from django.utils import timezone
from datetime import timedelta

class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=255)   # store hashed password ONLY
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    otp = models.CharField(max_length=6)
    attempt_count = models.PositiveIntegerField(default=0)    # OTP tries
    resend_count = models.PositiveIntegerField(default=0)     # OTP resends
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self, minutes=10):
        return timezone.now() > (self.created_at + timedelta(minutes=minutes))

    def __str__(self):
        return f"PendingUser({self.email})"


# from xml import dom
# from django.db import models
# from django.contrib.auth.models import User
# from hashtag.models import Hashtag
# from ckeditor.fields import RichTextField

# def superuser(): return User.objects.filter(is_superuser=True)

# choices = [('Mentor','mentor'),('Entreprenur','entreprenur'), ('Investor','Investor'),('Incubator','incubator'),('Schemes','schemes'),]

# # class UserType(models.Model):
# #     username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
# #     type = models.CharField(max_length=255, choices=choices, default=None)
# #     desc = RichTextField(default=None, blank=True)
# #     img = models.ImageField(max_length=255, default=None, upload_to='users/')
# #     phone = models.CharField(max_length=10, default=None)
#     # domain_expert = models.ForeignKey(Hashtag, default=None, on_delete=models.CASCADE, related_name='domain_expert', null=True)

# class Mentor(models.Model):
#     username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     desc = RichTextField(default=None, blank=True)
#     linkedin = models.CharField(max_length=255, blank=True)
#     portfolio = models.CharField(max_length=255, blank=True)
#     professional_mail = models.CharField(max_length=255, blank=True)
#     domain_expert = models.CharField(max_length=255, blank=True)
#     approved = models.BooleanField(default=False)

# class UsersType(models.Model):
#     username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     type = models.CharField(max_length=255, choices=choices, default=None)
#     desc = RichTextField(default=None, blank=True)
#     # img = models.ImageField(max_length=255, default=None, upload_to='users/')
#     phone = models.CharField(max_length=10, default=None)
#     # domain_expert = models.CharField(max_length=50, default=None)

# class Profile(models.Model):
#     username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
#     # bio = models.CharField(max_length=250,null=True)
#     # mobile_no = models.CharField(max_length=15,null=True)
#     entre = models.BooleanField(default=False)
#     mentor = models.BooleanField(default=False)
#     investor = models.BooleanField(default=False)
#     incubator = models.BooleanField(default=False)
#     partner = models.BooleanField(default=False)
#     job_seaker = models.BooleanField(default=False)

#     def __str__(self):
#         return self.username.username

# class Education(models.Model):
#     username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=40)

#     def __str__(self):
#         return self.name

# class Hobbies(models.Model):
#     username = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='hobby_name', null=True)

#     def __str__(self):
#         return self.name.name 
    
#     class Meta:
#         unique_together = ['username', 'name']
#         ordering = ['-id']

# class Skills(models.Model):
#     username = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.ForeignKey(Hashtag, on_delete=models.CASCADE, related_name='skill_name', null=True)

#     def __str__(self):
#         return self.name.name 

#     class Meta:
#         unique_together = ['username', 'name']
#         ordering = ['-id']

# class Interests(models.Model):
#     username = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.ForeignKey(Hashtag,on_delete=models.CASCADE, related_name='interest_name', null=True)

#     def __str__(self):
#         return self.name.name

#     class Meta:
#         unique_together = ['username', 'name']
#         ordering = ['-id']


# class Follow(models.Model):
#     username = models.ForeignKey(User, on_delete=superuser, to_field="username", related_name='follow_to', null=True)
#     following = models.ForeignKey(User, on_delete=superuser, related_name='followed_by', null=True)
    
#     def __str__(self):
#         return self.username.username

#     class Meta:
#         unique_together = ['username', 'following']

