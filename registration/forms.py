from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import CustomUser


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.TextInput(
        attrs={'autofocus': True}))

    def confirm_login_allowed(self, user): # is_active가 False인 경우에도 Login은 가능하도록 설정
        return None


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2',)