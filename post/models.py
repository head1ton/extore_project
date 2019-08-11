from django.db import models
from tagging.fields import TagField
from location_field.models.plain import PlainLocationField
from django.contrib.auth import get_user_model
from django.urls import reverse
from extore.models import Group


User = get_user_model()
class Post(models.Model):
    extore = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    image = models.ImageField(upload_to='timeline_photo/%Y/%m/%d')
    text = models.TextField()
    tags = TagField(blank=True)
    city = models.CharField(max_length=100, blank="")
    location = PlainLocationField(based_fields=['city'], zoom=7) # default="37.54965563216749,127.0469284057617"
    created = models.DateTimeField(auto_now_add=False)
    updated = models.DateTimeField(auto_now=True)
    like = models.ManyToManyField(User, related_name="like_post", blank=True)
    saved = models.ManyToManyField(User, related_name="saved_post", blank=True)

    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        return reverse('post:detail', args=[self.id])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0)

    def __str__(self):
        try:
            return self.author.username + "의 댓글"
        except AttributeError:
            return '비회원의 댓글'


    class Meta:
        ordering = ['-id']