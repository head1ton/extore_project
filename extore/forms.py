from django import forms
from .models import *

# class BoardForm(forms.ModelForm):
#     class Meta:
#         model = Board
#         fields = ['title']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'image']