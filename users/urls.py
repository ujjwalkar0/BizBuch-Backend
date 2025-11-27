# import imp
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from users.views import *


urlpatterns = [
    path('login/',obtain_auth_token),
    path('register/',RegisterView.as_view()),
    # path('logout/',LogoutView.as_view()),
    # path('in/<str:username>/',UserView.as_view()),
    # path('type/',UserTypeView.as_view()),
    # path('type/<str:type>',UserTypeView.as_view()),
    # path('follow/',FollowView.as_view()),
    # path('get/<str:name>/',GetMeView.as_view()),
    # path('mentors/',MentorView.as_view()),
    # path('mentors/<str:type>/',MentorView.as_view()),
]