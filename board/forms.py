from django import forms
from .models import *

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['category', 'title', 'text']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = ''
        self.fields['text'].widget = forms.TextInput()
        self.fields['text'].widget.attrs = {'class':'form-control','placeholder':'댓글을 입력하세요.'}
