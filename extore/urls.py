from django.urls import path
from .views import *

app_name='extore'

urlpatterns=[
    path('', group_list, name='extore_list'),
    path('detail/<int:group_id>/',group_detail, name='extore_detail'),
    path('create/', group_create, name='extore_create'),
    path('delete/', group_delete, name='extore_delete'),

]