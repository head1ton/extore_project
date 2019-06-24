from django.db import models

# Create your models here.
class Post(models.Model):
    author = models.CharField(max_length=50)
    image = models.ImageField(upload_to='timeline_photo/%Y/%m/%d')
    text = models.TextField()
    tags = models.