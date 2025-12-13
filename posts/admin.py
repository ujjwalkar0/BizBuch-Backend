from django.contrib import admin
from posts.models import Post, PostReport

# Admin Can Delete a Post after checking report
admin.site.register([Post, PostReport])