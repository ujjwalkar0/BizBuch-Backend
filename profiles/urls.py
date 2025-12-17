from django.urls import path

from profiles.views import *

urlpatterns = [
    path("me/", MyProfileAPIView.as_view()),
    path("", ProfileListAPIView.as_view()),
    path("<int:pk>/", ProfileDetailAPIView.as_view()),
    path("<int:pk>/follow/", FollowProfileAPIView.as_view()),
    path("<int:pk>/unfollow/", UnfollowProfileAPIView.as_view()),
    path("<int:pk>/followers/", FollowersListAPIView.as_view()),
    path("<int:pk>/following/", FollowingListAPIView.as_view()),
]
