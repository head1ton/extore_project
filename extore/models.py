from django.db import models
from accounts.models import User
from django.contrib.auth.models import Group

class Group(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, db_index=True, default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_user')
    member = models.ManyToManyField(User,related_name='group_members', blank=True)
    image = models.ImageField(upload_to='extore_images/%Y/%m/%d', blank=True, null=True)



    def __str__(self):
        return self.title