from django.urls import path
from .views.my_profile_api_view import MyProfileAPIView
from .views.profile_detail_api_view import ProfileDetailAPIView
from .views.profile_list_api_view import ProfileListAPIView

urlpatterns = [
    path("me/", MyProfileAPIView.as_view()),
    path("", ProfileListAPIView.as_view()),
    path("<int:pk>/", ProfileDetailAPIView.as_view()),
]
