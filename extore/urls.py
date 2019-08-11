from django.urls import path
from .views import *

app_name='extore'

urlpatterns=[
    path('', group_list, name='extore_list'),
    path('extore/detail/<int:group_id>/',group_detail, name='extore_detail'),
    path('extore/create/', group_create, name='extore_create'),
    path('extore/delete/<int:group_id>/', group_delete, name='extore_delete'),

]