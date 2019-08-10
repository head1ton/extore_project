from django.urls import path
from .views import board_create, board_list, board_detail, comment_update, comment_delete,comment_create

app_name = 'board'

urlpatterns = [
    path('create/<int:group_id>/', board_create, name='board_create'),
    path('list/<int:group_id>/', board_list, name='board_list'),
    path('detail/<int:board_id>/', board_detail, name='board_detail'),
    path('create/<int:board_id>/', comment_create, name='comment_create'),
    path('comment/update/<int:comment_id>/', comment_update, name='comment_update'),
    path('comment/delete/<int:comment_id>/', comment_delete, name='comment_delete'),
]