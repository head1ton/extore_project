from django import forms
from .models import *
# from django.forms.widgets import ClearableFileInput
#
#
# class CustomImageFieldWidget(ClearableFileInput):
#     template_with_clear = '<label for="%(clear_checkbox_id)s">%(clear)s %(clear_checkbox_label)s</label>'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image','text', 'tags','city', 'location', 'created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = ''
        self.fields['text'].label = ''
        self.fields['text'].widget.attrs = {'class':'form-control','placeholder':'내용을 입력하세요.'}
        self.fields['tags'].label = ''
        self.fields['tags'].widget.attrs = {'class':'form-control','placeholder': '태그를 입력하세요.'}
        self.fields['city'].label = ''
        self.fields['city'].widget.attrs = {'class':'form-control','placeholder': '위치를 추가하세요.(ex. Seoul)'}
        self.fields['location'].label = ''
        self.fields['location'].widget.attrs = {'class':'form-control','placeholder':'위도,경도'}
        self.fields['created'].widget.attrs = {'class':'form-control','placeholder':'ex) 2019-06-26'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = ''
        self.fields['text'].widget = forms.TextInput()
        self.fields['text'].widget.attrs = {'class':'form-control','placeholder':'댓글을 입력하세요.'}