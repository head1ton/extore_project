from django.db import models
from tagging.fields import TagField
from location_field.models.plain import PlainLocationField
from django.contrib.auth import get_user_model
from django.urls import reverse
# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    image = models.ImageField(upload_to='timeline_photo/%Y/%m/%d')
    text = models.TextField()
    tags = TagField(blank=True)
    city = models.CharField(max_length=100, blank="")
    location = PlainLocationField(based_fields=['city'], zoom=7)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    like = models.ManyToManyField(get_user_model(), related_name="like_post")
    saved = models.ManyToManyField(get_user_model(), related_name="saved_post")

    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        return reverse('photo:detail', args=[self.id])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0)

    def __str__(self):
        return self.author.username + "의 댓글"

    class Meta:
        ordering = ['-id']
