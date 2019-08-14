from django.urls import path
from .views import *

app_name = 'schedule'

urlpatterns = [
    path('', index, name='index'),
    path('create/', schedule_create, name='create'),
    path('list/<int:group_id>/', schedule_list, name='list'),
    path('update/<int:calendarevent_id>/', schedule_update, name='update'),
    path('delete/<int:calendarevent_id>/', schedule_delete, name='delete'),
    path('all_events/<int:group_id>/', all_events, name='all_events'),
]