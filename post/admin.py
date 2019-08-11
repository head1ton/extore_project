from django.contrib import admin

from .models import *

class CommentInline(admin.TabularInline):
    model = Comment

class PostOption(admin.ModelAdmin):
    list_display = ['id', 'author', 'city', 'created', 'updated']
    inlines = [CommentInline]

class CommentOption(admin.ModelAdmin):
    list_display = ['id', 'author', 'text']

admin.site.register(Post, PostOption)

admin.site.register(Comment, CommentOption)