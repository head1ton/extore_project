from django.contrib import admin
from django.urls import path
from .views import *

app_name = 'post'

urlpatterns = [
    path('list/', post_list, name='list'),
    path('create/', post_create, name='create'),
    path('detail/<int:post_id>/', post_detail, name='detail'),
    path('update/<int:post_id>/', post_update, name='update'),
    path('delete/<int:post_id>/', post_delete, name='delete'),
    path('tags/<tag>/', PostTaggedObjectList.as_view(), name='post_taggedlist'),
    path('comments/<int:post_id>/', comment_create, name='comment_create'),
    path('like/<int:post_id>/', post_like, name='post_like'),
    path('saved/<int:post_id>/', post_saved, name='post_saved'),
    path('comment/<int:comment_id>/', comment_like, name='comment_like'),
    path('last_memory/', last_memory, name='last_memory'),
    path('comment/update/<int:comment_id>/', comment_update, name='comment_update'),
    path('comment/delete/<int:comment_id>/', comment_delete, name='comment_delete'),
]