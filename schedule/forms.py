from django import forms
from .models import *

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'start', 'end']
        widget = {
            'start':forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M']),
            'end':forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M']),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = ''
        self.fields['title'].widget.attrs = {'class':'form-control', 'placeholder':'할 일을 입력하세요.'}
        self.fields['start'].widget.attrs = {'class':'form-control', 'placeholder':'시작일(ex. 2019-06-28 10:00'}
        self.fields['end'].widget.attrs = {'class':'form-control', 'placeholder':'종료일(ex. 2019-06-28 18:00'}