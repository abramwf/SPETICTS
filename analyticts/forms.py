from django import forms

from .models import Transcribe

class TranscribeForm(forms.ModelForm):
    class Meta:
        model = Transcribe
        fields = ['title', 'trans_result']

