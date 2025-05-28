from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Worker


class WorkerEditForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['image']


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
