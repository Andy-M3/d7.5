from allauth.account.forms import SignupForm, LoginForm, ChangePasswordForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Account
from django.core.mail import send_mail
from django.core.mail import mail_managers



class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        authors = get(name="authors")
        user.groups.add(authors)
        return user

class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_users = get(name="common users")
        user.groups.add(common_users)

        send_mail(
            subject='Welcome to our NewsPaper!',
            message=f'{user.username}, you have successfully registered!',
            from_email=None,
            recipient_list=[user.email],
        )
        return user
