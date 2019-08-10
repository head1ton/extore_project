from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from accounts.models import User
from extore.models import Group


class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, db_index=True)

    def __str__(self):
        return self.title


class Board(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categorys')
    group_id = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boardusers')
    text = RichTextUploadingField()
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.group} - {self.author}-{self.category}'

    class Meta:
        ordering = ['-created']


class Comment(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='comment_board')
    nickname = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='nicknames')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    like = models.ManyToManyField(User, related_name='comment_like', blank=True)

    def __str__(self):
        return f'{self.nickname.username}님의 댓글'
