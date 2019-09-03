from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from accounts.models import User


class Group(models.Model):
    title = models.CharField(max_length=15)
    slug = models.SlugField(max_length=50, unique=True, allow_unicode=True, db_index=True, default="")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_groups')
    member = models.ManyToManyField(User, related_name='members_groups', blank=True)
    image = models.ImageField(upload_to='group_images/%Y/%m/%d', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class InviteStatus(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invites')
    invited = models.ManyToManyField(User, related_name='invited', blank=True)
    accepted = models.ManyToManyField(User, related_name='accepted', blank=True)
    rejected = models.ManyToManyField(User, related_name='rejected', blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group.title


class InviteDate(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitedDate')
    invited = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitedDate')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.invited.last_name}{self.invited.first_name} invited from {self.group.title} in {self.created}'