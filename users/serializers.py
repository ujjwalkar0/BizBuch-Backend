from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password',
                  'first_name', 'last_name', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        return data
    
    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data.get('first_name', ''),
            last_name = validated_data.get('last_name', ''),
            password = validated_data['password']
        )
        return user



# from asyncore import read
# from dataclasses import field, fields
# from pyexpat import model
# from rest_framework.serializers import ModelSerializer, StringRelatedField
# from django.contrib.auth.models import User
# from users.models import *


# class MentorSerializer(ModelSerializer):
#     class Meta:
#         model = Mentor
#         # fields = '__all__'
#         exclude = ('approved',)

# class UserTypeSerializer(ModelSerializer):
#     class Meta:
#         model = UsersType
#         fields = '__all__'

# class ProfileSerializer(ModelSerializer):
#     class Meta:
#         model = Profile
#         exclude = ('username',)

# class UserSerializer(ModelSerializer):    
#     class Meta:
#         model = User
#         fields = [
#             'first_name',
#             'last_name',
#             'email',
#             'username',
#         ]

# class FollowSerializer(ModelSerializer):
#     class Meta:
#         model = Follow
#         fields = ['following']
        
# class HobbiesSerializer(ModelSerializer):
#     class Meta:
#         model = Hobbies
#         fields = '__all__'

# class InterestsSerializer(ModelSerializer):
#     class Meta:
#         model = Interests
#         fields = '__all__'
    
# class SkillsSerializer(ModelSerializer):
#     class Meta:
#         model = Skills
#         fields = '__all__'

# class EducationSerializer(ModelSerializer):
#     class Meta:
#         model = Education
#         fields = '__all__'