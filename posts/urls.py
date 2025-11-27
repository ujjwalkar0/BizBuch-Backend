# from django.urls import path
# from posts.views import *

# urlpatterns=[
#     path('comment/',CommentView.as_view()),
#     path('commentview/<int:pk>',CommentViewToALL.as_view()),
#     path('',PostsViewSet.as_view()),
#     path('<str:catagory>/',PostsViewSet.as_view()),
#     # path('catagory/<str:catagory>/',PostsByCategory.as_view()),
#     path('tag/<str:catagory>/',PostByTagView.as_view()),
#     path('views/<int:id>/',PostsViewToALL.as_view()),
#     path('hashtag/<str:hashtag>/',ViewsByHashtag.as_view()),
#     path('mypost/<str:catagory>/',MyArticleView.as_view()),
#     path('like/<int:id>/', Like.as_view())
# ]