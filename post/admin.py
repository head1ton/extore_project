from django.contrib import admin

from .models import *

class PostOption(admin.ModelAdmin):
    list_display = ['author', 'city', 'created', 'updated']

admin.site.register(Post, PostOption)