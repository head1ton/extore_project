from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.urls import reverse

from extore.models import Group

User = get_user_model()

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, db_index=True)

    def __str__(self):
        return self.title


class Board(models.Model):
    extore = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='boards')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='boards')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    title = models.CharField(max_length=20, blank=True)
    text = RichTextUploadingField()
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.author}-{self.category}'

    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        return reverse('board:detail', args=[self.id])


class Comment(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='comments')
    nickname = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='board_comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.nickname.username}님의 댓글'

    class Meta:
        ordering = ['-created']
