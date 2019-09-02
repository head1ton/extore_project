from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    message = models.TextField(blank=True)
    profile = models.ImageField(upload_to='user_images/profile/%Y/%m/%d')
    phone_number = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.username
