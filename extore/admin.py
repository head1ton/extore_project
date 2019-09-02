from django.contrib import admin
from .models import Group, InviteStatus, InviteDate
# Register your models here.

class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug']
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Group, GroupAdmin)

admin.site.register(InviteStatus)

admin.site.register(InviteDate)
