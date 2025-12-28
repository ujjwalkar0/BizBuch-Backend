from django.urls import path
from posts.views import *

urlpatterns = [

    # posts
    path("", PostListCreateView.as_view(), name="post-list-create"),
    path("<int:pk>/", PostRetrieveUpdateDeleteView.as_view(), name="post-detail"),

    # comments
    path("<int:post_id>/comments/", CommentListCreateView.as_view(), name="comment_list_create"),
    path("comments/<int:pk>/", CommentRetrieveUpdateDeleteView.as_view(), name="comment_detail"),

    # Likes
    path("<int:post_id>/likes/", PostLikeListCreateView.as_view(), name="post_like_list_create"),
    path("likes/<int:pk>/", PostLikeDeleteView.as_view(), name="post_like_delete"),
    
    # Report
    path("<int:post_id>/report/", PostReportListCreateView.as_view(), name="post_report"),

]
