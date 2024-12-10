from django import forms


class RegisterForm(forms.Form):
    """
    Form for user registration.
    """
    username = forms.CharField(max_length=70)
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    email = forms.EmailField()


class LoginForm(forms.Form):
    """
    From for user log in.
    """
    username = forms.CharField(max_length=70)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput())


class CreateGroupForm(forms.Form):
    """
    Form for group create.
    """
    name = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255)
    description = forms.CharField(max_length=500)
    

class LogInGroupForm(forms.Form):
    """
    Form for group log in.
    """
    password = forms.CharField(max_length=255)


class CreateTaskForm(forms.Form):
    """
    Form for Task create.
    """
    photo = forms.ImageField()
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the task title'})
    )
    discription = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter task description', 'rows': 5})
    )
