from django.urls import path
from .views import (
    OnboardingStatusAPIView,
    TopicListAPIView,
    SubmitTopicsAPIView
)

urlpatterns = [
    path("status/", OnboardingStatusAPIView.as_view()),
    path("topics/", TopicListAPIView.as_view()),
    path("topics/submit/", SubmitTopicsAPIView.as_view()),
]
