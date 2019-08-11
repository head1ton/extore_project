from django.urls import path
from .views import *

app_name = 'board'

urlpatterns = [
    path('create/', board_create, name='board_create'),
    path('list/', board_list, name='board_list'),
    path('detail/<int:board_id>/', board_detail, name='board_detail'),
    path('comments/<int:board_id>/', comment_create, name='comment_create'),
    path('comment/<int:comment_id>/', comment_like, name='comment_like'),
    path('comment/update/<int:comment_id>/', comment_update, name='comment_update'),
    path('comment/delete/<int:comment_id>/', comment_delete, name='comment_delete'),
]