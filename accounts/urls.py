from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView


app_name = 'accounts'

urlpatterns = [
    path('search/', user_search, name='search'),
    path('invite/', user_invite, name='invite'),
    path('accept/<int:inviteStatus_id>/', user_accept, name='accept'),
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]