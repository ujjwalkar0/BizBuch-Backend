from django.urls import path

from profiles.views import *

urlpatterns = [
    path("me/", MyProfileAPIView.as_view()),
    path("me/work-experience/", WorkExperienceCreateAPIView.as_view()),
    path("me/work-experience/<int:pk>/", WorkExperienceUpdateDeleteAPIView.as_view()),
    path("me/education/", EducationCreateAPIView.as_view()),
    path("me/education/<int:pk>/", EducationUpdateDeleteAPIView.as_view()),
    path("connections/", ConnectionsAPIView.as_view()),
    path("", ProfileListAPIView.as_view()),
    path("<int:user_id>/", ProfileDetailAPIView.as_view()),
    path("<int:pk>/follow/", FollowProfileAPIView.as_view()),
    path("<int:pk>/unfollow/", UnfollowProfileAPIView.as_view()),
    path("<int:pk>/followers/", FollowersListAPIView.as_view()),
    path("<int:pk>/following/", FollowingListAPIView.as_view()),
]
