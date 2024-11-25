from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=70)
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    email = forms.EmailField()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=70)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput())


class CreateGroupForm(forms.Form):
    name = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    description = forms.CharField(max_length=500)
    

class LogInGroupForm(forms.Form):
    password = forms.CharField(max_length=255)