from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    UserAdmin.fieldsets[1][1]['fields'] += ('profile', 'message', 'phonenumber')
    UserAdmin.add_fieldsets += (
        (('Additional Info'), {'fields':('profile','message', 'phonenumber')}),
    )

admin.site.register(User, CustomUserAdmin)