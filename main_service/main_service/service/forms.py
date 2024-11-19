from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=70)
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    email = forms.EmailField()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=70)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput())
    