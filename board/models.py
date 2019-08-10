from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

from accounts.models import User

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, db_index=True)

    def __str__(self):
        return self.title



class Board(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categorys')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boardusers')
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, db_index=True)
    text = RichTextUploadingField()
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    group = models.IntegerField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']

class Comment(models.Model):
    # Todo : 댓글 남기기를 위해서 form필요
    # Todo : 뷰 처리는 Document의 뷰

    document = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0) # ManyToMany
    dislike = models.IntegerField(default=0)

    def __str__(self):
        return (self.author.username if self.author else "무명") + "의 댓글"