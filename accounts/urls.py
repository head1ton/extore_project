from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('search/', user_search, name='search'),
]