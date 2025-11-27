from django.db import models
from django.contrib.auth.models import User
# from hashtag.models import Hashtag
# from catagories.models import Catagory 
from ckeditor.fields import RichTextField

class Posts(models.Model):
    username = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    title = models.CharField(max_length=140)
    short_desc = models.CharField(max_length=500, default=None)
    desc = RichTextField()
    # catagory = models.ForeignKey(Catagory, on_delete=models.CASCADE, max_length=50)
    # attachment = models.ImageField(upload_to='posts/', null=True)
    # hashtag = models.ManyToManyField(Hashtag, related_name='plans')
    post_time = models.TimeField(auto_now=True, null=True)
    post_date = models.DateField(auto_now=True, null=True)
    comment= models.IntegerField(default=0)
    like = models.IntegerField(default=0)
    unlike = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title    
    
    class Meta:
        ordering = ['-id']

class Likes(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('username', 'posts',)

    def __str__(self):
        return self.posts.title
    
    def save(self, *args, **kwargs):
        post = Posts.objects.get(id=self.posts.id)
        post.like = post.like+1
        super(Likes, self).save(*args, **kwargs)
        post.save()

class UnLikes(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('username', 'posts',)

    def __str__(self):
        return self.posts.title
    
    def save(self, *args, **kwargs):
        post = Posts.objects.get(id=self.posts.id)
        post.unlike = post.unlike+1
        post.save()
        super(UnLikes, self).save(*args, **kwargs)

 
class Comments(models.Model):
    username = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    posts = models.ForeignKey(Posts, on_delete=models.CASCADE)
    comment = models.CharField(max_length=220)
    post_time = models.TimeField(auto_now=True, null=True)
    post_date = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return self.comment
    
    def save(self, *args, **kwargs):
        post = Posts.objects.get(id=self.posts.id)
        post.comment = post.comment+1
        super(Comments, self).save(*args, **kwargs)
        post.save()

class Share(models.Model):
    pass
