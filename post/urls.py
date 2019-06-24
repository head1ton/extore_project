from django.contrib import admin
from django.urls import path
from .views import *

app_name = post

urlpatterns = [
    path('', main_page, name='mainpage'),
    path('post/list/', post_list, name='list'),
]