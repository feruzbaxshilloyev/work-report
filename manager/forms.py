from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from decimal import Decimal

from django.core.exceptions import ValidationError
from manager.models import Message, MonthlyPayment, ManagerProfile
from worker.models import Worker


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


class ChangeManagerProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email manzil",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email kiriting',
            'required': 'required'
        })
    )

    class Meta:
        model = ManagerProfile
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'image': 'Profil rasmi'
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['email'].initial = user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("Bu email manzil allaqachon ishlatilmoqda.")
        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
                instance.save()
        return instance


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Yangi parol",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yangi parol kiriting',
            'required': 'required'
        })
    )
    new_password2 = forms.CharField(
        label="Parolni tasdiqlash",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni qayta kiriting',
            'required': 'required'
        })
    )


class MonthlyPaymentForm(forms.ModelForm):
    class Meta:
        model = MonthlyPayment
        fields = ['worker', 'summa', 'sana']
        widgets = {
            'sana': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'summa': forms.NumberInput(attrs={'class': 'form-control'}),
            'worker': forms.Select(attrs={'class': 'form-select'}),
        }


class TolowForm(forms.ModelForm):
    worker = forms.ModelChoiceField(
        queryset=Worker.objects.none(),
        label="Ishchi",
        widget=forms.HiddenInput(),  # worker maydoni yashirin, chunki w_id orqali berilgan
        required=True
    )
    summa = forms.DecimalField(
        label="To‘lov summasi (so‘m)",
        min_value=Decimal('0.01'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'Summani kiriting',
            'required': 'required'
        })
    )
    sana = forms.DateField(
        label="To‘lov sanasi",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required'
        })
    )

    class Meta:
        model = MonthlyPayment
        fields = ['worker', 'summa', 'sana']

    def __init__(self, worker_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if worker_id:
            # Faqat berilgan worker_id bilan ishchi tanlanadi
            self.fields['worker'].queryset = Worker.objects.filter(worker_id=worker_id)
            self.fields['worker'].initial = Worker.objects.filter(worker_id=worker_id).first()

    def clean(self):
        cleaned_data = super().clean()
        worker = cleaned_data.get('worker')
        summa = cleaned_data.get('summa')

        if worker and summa:
            if summa <= 0:
                raise ValidationError("To‘lov summasi musbat bo‘lishi kerak.")
            if summa > worker.qoldiq:
                raise ValidationError(
                    f"To‘lov summasi ishchining qoldiq summasidan ({worker.qoldiq} so‘m) ko‘p bo‘lishi mumkin emas.")

        return cleaned_data
