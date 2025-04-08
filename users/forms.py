from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.hashers import make_password


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')
        help_texts = {
            'username': CustomUser._meta.get_field('username').help_text,
            'password1': UserCreationForm().fields['password1'].help_text,
            'password2': UserCreationForm().fields['password2'].help_text,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'vTextField'})  # This is what Django admin expects

class CustomUserChangeForm(UserChangeForm):
    new_password = forms.CharField(
        label="New Password",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        help_text="Leave blank if you don’t want to change the password."
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'input'})
        if 'password' in self.fields:
            self.fields['password'].help_text = None
            self.fields['password'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.password = make_password(new_password)
        if commit:
            user.save()
        return user

