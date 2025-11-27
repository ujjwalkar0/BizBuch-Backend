# from django.shortcuts import get_list_or_404
# from posts.models import *
# from posts.serializers import *
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.response import Response
# from rest_framework.authentication import TokenAuthentication
# # from hashtag.models import TagFollow
# # from users.models import Follow, Hobbies, Interests, Skills
# # from noti.models import Noti
# import time
# # from docType.docType import detect_class
# # from catagories.models import Catagory

# class PostsViewToALL(APIView):
#     permission_classes = (AllowAny,)

#     def get(self, request, id):
#         posts = Posts.objects.get(id=id)
#         print(posts)
#         serializer = PostDetailsSerializer(posts)
#         return Response(serializer.data)

# # class PostsByCategory(APIView):
# #     permission_classes = (AllowAny,)

# #     def get(self, request, category):
# #         posts = Posts.objects.filter(category=category)
# #         serializer = PostSerializer(posts, many=True)
# #         return Response(serializer.data)

# class CommentViewToALL(APIView):
#     permission_classes = (AllowAny,)

#     def get(self, request,pk, format=None):
#         posts = Posts.objects.get(id=pk)
#         comments = Comments.objects.filter(posts=posts)
#         serializer = CommentSerializer(comments, many=True)
#         return Response(serializer.data)

# class Like(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def post(self, request, id, *args, **kwargs):
#         try:
#             post = Posts.objects.get(id=id)
#         except Posts.DoesNotExist:
#             return Response(status=404)
        
#         try:
#             user = User.objects.get(username=self.request.user)
#         except User.DoesNotExist:
#             return Response(status=404)

#         like = Likes.objects.create(username=user, posts=post)
#         # like.save()
#         # print(id,self.request.user)
#         # Like.objects.create(username=self.request.user,) 
#         return Response(status=200)

# class CommentView(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def post(self, request, format=None):
#         print(request.data)
#         username = User.objects.get(username=request.user)
#         posts = Posts.objects.get(id=request.data["id"])
#         comment = request.data["addComment"]

#         Comments.objects.create(
#             username = username,
#             posts = posts,
#             comment = comment
#         )
#         curr_time = time.localtime()
#         curr_clock = time.strftime("%H:%M:%S", curr_time)

#         noti_to_user = posts.username
#         msg = f"{username.first_name} {username.last_name} commented on {posts.title} at {curr_clock}"
#         post = Posts.objects.get(id=posts.id)

#         Noti.objects.create(
#             username=noti_to_user,
#             noti = msg,
#             post=post
#         )
#         return Response({"Comment":"commented"})

# class PostsViewSet(APIView):
#     permission_classes = (AllowAny,)
#     authentication_classes = (TokenAuthentication,)

#     def get(self, request, catagory=None, format=None):
#         # followings = Follow.objects.filter(username=request.user)
#         # post = Posts.objects.filter(username=request.user)
#         print(request.user)

#         if request.user.is_authenticated:
#             global tags
#             tags = TagFollow.objects.filter(follower=User.objects.get(username=request.user))
#             print([i['name'] for i in tags.values('name')])
#             posts = Posts.objects.filter(hashtag__in=[i['name'] for i in tags.values('name')])

#             print([i for i in posts])
#         else:
#             posts = Posts.objects.all()
        
#         serializer = PostSerializer(posts, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         print(request.data)
#         username = User.objects.filter(username=request.user).first()
#         title = request.data["title"]
#         desc = request.data["desc"]
#         short_desc = request.data["shrtdesc"]
#         catagory = Catagory.objects.get(name=request.data["catagory"]) #request.data["catagory"]
#         # hasht = Hashtag.objects.filter(name__in=request.data["hashtag"])


#         # if detect_class(desc)!='business':
#         #     return Response({"Response":"Your Post is not a related to business"})
        

#         a = Posts.objects.create(
#             username = username,
#             title = title,
#             desc = desc,
#             catagory = catagory,
#             short_desc = short_desc,
#         )
#         # a.hashtag.set(hasht)
#         a.save()

#         return Response({"Response":"Success"})

# class PostByTagView(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def get(self, request, catagory=None, format=None):
#         hashtags = TagFollow.objects.filter(follower=request.user).values('name')
#         hobbies = Hobbies.objects.filter(username=request.user)
#         skills = Skills.objects.filter(username=request.user)
#         interests = Interests.objects.filter(username=request.user)
#         posts2 = Posts.objects.filter(
#            hashtag__in=[i['name'] for i in hashtags]
#            +[i.name.name for i in hobbies]
#            +[i.name.name for i in interests]
#            +[i.name.name for i in skills]
#         ).filter(catagory=catagory).distinct()

#         serializer = PostSerializer(posts2, many=True)
#         return Response(serializer.data)


# class ViewsByHashtag(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)

#     def get(self, requests, hashtag):
#         tags = Hashtag.objects.filter(name=hashtag)
#         post = Posts.objects.filter(hashtag__in = [i for i in tags])
#         serializer = PostSerializer(post, many=True)
#         return Response(serializer.data)

# class MyArticleView(APIView):
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (TokenAuthentication,)
    
#     def get(self, requests, catagory):
#         posts = Posts.objects.filter(username=requests.user).filter(catagory=catagory)
#         serializer = PostSerializer(posts, many=True)
#         return Response(serializer.data)


# #
# # class PostsViewSet(APIView):
# #     permission_classes = (IsAuthenticated,)
# #     authentication_classes = (TokenAuthentication,)
    
# #     def get(self, request, pk=None):
# #         if pk is None:
# #             posts = Posts.objects.all()
# #             serializer = PostSerializer(posts, many=True)
# #             return Response(serializer.data)
# #         else:
# #             posts = Posts.objects.filter(id=pk)
# #             serializer = PostSerializer(posts, many=True)
# #             return Response(serializer.data)

# #     def post(self, request):
# #         username = User.objects.get(username=request.user)
# #         hashtag = Hashtag.objects.filter(hashtag__in=request.data["hashtag"])
# #         posts = Posts.objects.create(
# #             username = username,
# #             title = request.data["title"],
# #             desc = request.data["desc"],
# #         )
# #         posts.hashtag.set(hashtag)
# #         posts.save()
# #         return Response({"Response":"Post Created"},status=status.HTTP_201_CREATED)