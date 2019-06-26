from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    message = models.TextField(blank=True)
    profile = models.ImageField(upload_to='user_images/profile/%Y/%m/%d')