from django.urls import path
from activity.views import (
    ActivityListView,
    ActivityMarkReadView,
    ActivityMarkAllReadView,
    ActivityLogView
)

urlpatterns = [
    path("notifications/", ActivityListView.as_view(), name="activity-list"),
    path("<int:pk>/read/", ActivityMarkReadView.as_view(), name="activity-read"),
    path("read-all/", ActivityMarkAllReadView.as_view(), name="activity-read-all"),
    path("log/", ActivityLogView.as_view(), name="activity-log"),
]
