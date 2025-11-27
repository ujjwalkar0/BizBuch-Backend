from rest_framework.generics import CreateAPIView
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.get_or_create(user=user)

# from django.shortcuts import render
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import permissions
# from django.contrib.auth.models import User
# # from hashtag.models import Hashtag
# from django.http import Http404
# from rest_framework.authentication import TokenAuthentication
# from users.models import *
# from users.serializers import *
# from django.db.utils import IntegrityError
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
# from rest_framework import status

# class MentorView(APIView):
#     permission_classes = (permissions.AllowAny,)  
#     authentication_classes = (TokenAuthentication,)

#     def get(self, request, type=None, *args, **kwargs):
#         # if type is None:
#         #     data = Mentor.objects.all()
#         # else:
#         mentors = Mentor.objects.all() #filter(domain_expert=type)        
#         serializer = MentorSerializer(mentors, many=True)
    
#         print(serializer.data)

#         # if serializer.is_valid():
#         #     return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.data)

#         # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#     def post(self, request, format=None):
#         request.data["username"] = User.objects.get(username=request.user).id
#         serializer = MentorSerializer(data=request.data)
#         print(serializer.is_valid())
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):
#     permission_classes = (permissions.AllowAny,)  
#     authentication_classes = (TokenAuthentication,)

#     def post(self, request, *args, **kwargs):
#         serializer = ObtainAuthToken.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key})

# class RegisterView(APIView):
#     # Anyone Can Register
#     permission_classes = (permissions.AllowAny,)  
#     def post(self, request, format=None):
#         # Collect Data from the Form
#         username = request.data["username"]
#         password = request.data["password"]
#         confirm_password = request.data["confirm_password"]
#         first_name = request.data["first_name"]
#         last_name = request.data["last_name"]
#         email = request.data["email"]

#         # Check If username Already exist or Not
#         if User.objects.filter(username=username):
#             return Response({"Message":"Username Already Exist"})

#         # Check If email Already exist or Not
#         if User.objects.filter(email=email):
#             return Response({"Message":"We already have an user with this email address"})

#         # Check If password and Confirm Password same or Not
#         if password!=confirm_password:
#             return Response({"Message":"Password Not Matched"})

#         # Now Create the User
#         user = User.objects.create(
#             username = username,
#             first_name = first_name,
#             last_name = last_name,
#             email = email,
#         )

#         # Set password for the User
#         user.set_password(password)
        
#         #Save User to the Database
#         user.save()
#         # Profile.objects.create(username = User.objects.get(username = username))

#         token, created = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key})

#         # return Response({"Message":"User Created"})

# class LogoutView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def delete(self, request, format=None):
#         request.user.auth_token.delete()
#         return Response({"Response":"Logout"})

# class UserTypeView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)


#     def get(self, request, type=None, format=None):
#         if type is None:
#             profile = UsersType.objects.get(username=request.user)
#             return Response({"type":profile.type})
#         data = UsersType.objects.filter(type=type)
#         serializer = UserTypeSerializer(data, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         profile = UsersType.objects.create(username=request.user, type = request.data["type"])
#         profile.save()
#         return Response({"MSG":"Done"})

# class GetUserProfile(APIView):
#     def get(self, request, type, *args, **kwargs):
#         Profile.objects.filter()

# class UserView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def get(self, request, username=None, format=None):
#         if username==None:
#             username=request.user
#         username = User.objects.get(username=username)
#         first_name = username.first_name
#         last_name = username.last_name
#         full_name = username.get_full_name()
#         user = username.username
#         profile = Profile.objects.filter(username=username).first()
#         hobbies = [i.name.name for i in Hobbies.objects.filter(username=username)]
#         interests = [i.name.name for i in Interests.objects.filter(username=username)]
#         skills = [i.name.name for i in Skills.objects.filter(username=username)]
#         follow = Follow.objects.filter(username=request.user, following=username).first()
        
#         if request.user==username:
#             follows = "Edit Profile"
#         elif follow:
#             follows="Following"
#         else:
#             follows="Follow"

#         return Response({
#             "name":full_name,
#             "first_name":first_name,
#             "last_name":last_name,
#             "username":user,
#             "bio":profile.bio,
#             "mobile_no":profile.mobile_no,
#             "hobbies":hobbies,
#             "interests":interests,
#             "skills":skills,
#             "entre":profile.entre,
#             "mentor":profile.mentor,
#             "inv":profile.inventor,
#             "job":profile.job_seaker,
#             "follow":follows
#         })

#     def put(self, request, username, format=None):
#         print(request.data)

#         if request.data["fname"]!='':
#             username = User.objects.get(username=request.user)
#             username.first_name = request.data["fname"]
#             username.save()

#         if request.data["lname"]!='':
#             username = User.objects.get(username=request.user)
#             username.last_name = request.data["lname"]
#             username.save()

#         if request.data["bio"]!='':
#             profile = Profile.objects.get(username=request.user)
#             profile.bio = request.data["bio"]
#             profile.save()
        
#         if request.data["entre"]!="":
#             profile = Profile.objects.get(username=request.user)
#             profile.entre = request.data["entre"]=="true"
#             profile.save()
        
#         if request.data["mentor"]=="true":
#             profile = Profile.objects.get(username=request.user)
#             profile.mentor = request.data["mentor"]=="true"
#             profile.save()
        
#         if request.data["inv"]=="true":
#             profile = Profile.objects.get(username=request.user)
#             profile.inventor = request.data["inv"]=="true"
#             profile.save()
        
#         if request.data["job"]=="true":
#             profile = Profile.objects.get(username=request.user)
#             profile.job_seaker = request.data["job"]=="true"
#             profile.save()
        
#         if request.data["mobile_no"]!='':
#             profile = Profile.objects.get(username=request.user)
#             profile.mobile_no = request.data["mobile_no"]
#             profile.save()
        
#         for i in request.data["hobbies"]:
#             try:
#                 hoby = Hobbies.objects.create(
#                     username=request.user,
#                     name = Hashtag.objects.get(name=i)
#                 )
#                 hoby.save()
#             except IntegrityError:
#                 pass
        
#         for i in request.data["interests"]:
#             try:
#                 hoby = Interests.objects.create(
#                     username=request.user,
#                     name = Hashtag.objects.get(name=i)
#                 )
#                 hoby.save()
#             except IntegrityError:
#                 pass
        
#         for i in request.data["skills"]:
#             try:
#                 hoby = Skills.objects.create(
#                     username=request.user,
#                     name = Hashtag.objects.get(name=i)
#                 )
#                 hoby.save()
#             except IntegrityError:
#                 pass
        
        
#         return Response({"Success":"Success"})

# # class IsFollowView(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #     authentication_classes = (TokenAuthentication,)

# #     def get(self, requests):
# #         user = User.objects.get(username=requests.user)
# #         user = User.objects.get(username=requests.user)



# # class FollowView(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #     authentication_classes = (TokenAuthentication,)

# #     def get(self, request, username=None, format=None):
# #         user = User.objects.get(username=request.user)
# #         follow = Follow.objects.filter(username=user)
# #         users = User.objects.all().exclude(username__in=[i.following for i in follow]+[i.username for i in follow])
# #         serializer = UserSerializer(users, many=True)
# #         return Response(serializer.data)

# #     def post(self, requests):
# #         user = User.objects.get(username=requests.user)
# #         follow = User.objects.get(username=requests.data["followp"])
# #         try:
# #             Follow.objects.create(username=user, following=follow)
# #             return Response({"Response","Followed"})
# #         except IntegrityError:
# #             return Response({"Response","Already Followed"})

# #     def delete(self,requests):
# #         user = User.objects.get(username=requests.user)
# #         follow = User.objects.get(username=requests.data["followp"])
# #         Follow.objects.filter(username=user, following=follow).delete()
# #         return Response({"Response","Unfollowed"})


# # class GetMeView(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #     authentication_classes = (TokenAuthentication,)

# #     def get(self, request, name):
# #         if name=="followings":
# #             followers = Follow.objects.filter(username=request.user)
# #             user = User.objects.filter(username__in=[i.following for i in followers])
# #             serializer = UserSerializer(user, many=True)
# #             return Response(serializer.data)

# #         if name=="followers":
# #             followers = Follow.objects.filter(following=request.user)
# #             print(followers)
# #             user = User.objects.filter(username__in=[i.username for i in followers])
# #             serializer = UserSerializer(user, many=True)
# #             return Response(serializer.data)

# # class FollowHashTag(APIView):
# #     permission_classes = (permissions.IsAuthenticated,)
# #     authentication_classes = (TokenAuthentication,)

# #     def post(self, requests):
# #         user = User.objects.get(requests.user)
# #         follow = User.objects.get(requests.data["follow"])
# #         Follow.objects.create(user=user, follow=follow)
# #         return Response({"Response","Followed"})


#         # username.first_name = request.data["first_name"]
#         # username.last_name = request.data["last_name"]
#         # last_name = username.last_name
#         # full_name = username.get_full_name()
#         # profile = Profile.objects.filter(username=username).first()
#         # hobbies = [i.name.name for i in Hobbies.objects.filter(username=username)]
#         # interests = [i.name.name for i in Interests.objects.filter(username=username)]
#         # skills = [i.name.name for i in Skills.objects.filter(username=username)]


#             # "user":self.get_data(username, User, UserSerializer), 
#             # "profile":self.get_data(username, Profile,ProfileSerializer),
#             # "hobbies":self.get_data(username, Hobbies, HobbiesSerializer),
#             # "interests":self.get_data(username, Interests, InterestsSerializer),
#             # "skills":self.get_data(username, Skills, SkillsSerializer),
#             # "education":self.get_data(username, Education, EducationSerializer),
#             # })

#     # def post(self, request, obj=None, format=None):
#     #     if obj == "hobbies":            
#     #         for i in request.data["name"]:
#     #             try:
#     #                 tag = Hashtag.objects.get(name=i)
#     #                 Hobbies.objects.create(
#     #                     username=request.user,
#     #                     name = tag
#     #                 )
#     #             except Hashtag.DoesNotExist:
#     #                 return Response({"Response":f"Create {i} First"})
#     #         return Response({"Response":f"Hobbies Created"})


#     #     if obj == "interests":            
#     #         for i in request.data["name"]:
#     #             try:
#     #                 tag = Hashtag.objects.get(name=i)
#     #                 Interests.objects.create(
#     #                     username=request.user,
#     #                     name = tag
#     #                 )
#     #             except Hashtag.DoesNotExist:
#     #                 return Response({"Response":f"Create {i} First"})
#     #         return Response({"Response":f"Interests Created"})

#     #     if obj == "skills":            
#     #         for i in request.data["name"]:
#     #             try:
#     #                 tag = Hashtag.objects.get(name=i)
#     #                 Skills.objects.create(
#     #                     username=request.user,
#     #                     name = tag
#     #                 )
#     #             except Hashtag.DoesNotExist:
#     #                 return Response({"Response":f"Create {i} First"})
#     #         return Response({"Response":f"Skills Created"})

#     # def put(self,request):
#     #     user = self.get_object(request.user.id)
#     #     profile = Profile.objects.filter(username = user)
#     #     serializer = UserSerializer(profile)
#     #     return Response(serializer.data)

#     #     # Incomplete
    
#     # def delete(self, request, obj=None, format=None):
#     #     if obj == "hobbies":            
#     #         for i in request.data["name"]:
#     #             try:
#     #                 tag = Hashtag.objects.get(name=i)
#     #                 a = Hobbies.objects.filter(
#     #                     username=request.user,
#     #                     name = tag
#     #                 )
#     #                 print(a)
#     #                 if a.count()==0:
#     #                     return Response({"Response":f"{i} Not exist"})
#     #                 a.delete()
#     #             except Hashtag.DoesNotExist:
#     #                 return Response({"Response":f"{i} Not exist"})
#     #         return Response({"Response":f"Hobbies Deleted"})


#     #     if obj == "interests":
#     #         flag = 0            
#     #         for i in request.data["name"]:
#     #             try:
#     #                 tag = Hashtag.objects.get(name=i)
#     #                 a = Interests.objects.filter(
#     #                     username=request.user,
#     #                     name = tag
#     #                 )
#     #                 if a.count()==0:
#     #                     flag = 1
#     #                 a.delete()
#     #             except Hashtag.DoesNotExist:
#     #                 return Response({"Response":f"{i} Not exist"})
#     #         if flag==1:
#     #             return Response({"Response":f"Interests Created"})
#     #         else:
#     #             return Response({"Response":f"Interests Not exist"})

#     #     if obj == "skills":            
#     #         for i in request.data["name"]:
#     #             try:
#     #                 tag = Hashtag.objects.get(name=i)
#     #                 a = Skills.objects.filter(
#     #                     username=request.user,
#     #                     name = tag
#     #                 )
#     #                 if a.count()==0:
#     #                     return Response({"Response":f"{i} Not exist"})
#     #                 a.delete()
#     #             except Hashtag.DoesNotExist:
#     #                 return Response({"Response":f"{i} Not exist"})
#     #         return Response({"Response":f"Skills Created"})
