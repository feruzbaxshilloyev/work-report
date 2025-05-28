from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from manager.models import Message


class ManagerRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Parolni qayta kiriting")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")
        if p1 != p2:
            raise forms.ValidationError("Parollar mos emas")
        return cleaned_data


class ManagerLoginForm(AuthenticationForm):
    pass


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sarlavha', 'matn']
        widgets = {
            'sarlavha': forms.TextInput(attrs={'class': 'form-control'}),
            'matn': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class ProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(
        label='Parol',
        widget=forms.PasswordInput,
        required=False,
        help_text="Parolni o'zgartirish uchun kiriting, aks holda bo'sh qoldiring."
    )
    image = forms.ImageField(label="Profil rasmi", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)

        password = self.cleaned_data.get('password')
        if password and password != '':
            user.set_password(password)

        if commit:
            user.save()
        return user
