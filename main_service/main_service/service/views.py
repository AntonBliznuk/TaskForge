import requests
import jwt

from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
from . import forms
from decouple import config


def login_support(request, username, password):
    data_to_api = {
        'username': username,
        'password': password,
    }
    response = requests.post(settings.GET_TOKENS, data=data_to_api)
    if response.status_code == 200:
        decoded = jwt.decode(response.json()['access'], config('SIGNING_KEY'), algorithms=config('ALGORITHM'))

        response_user_data = requests.post(settings.GET_DATA_BY_ID, data={'user_id': decoded['user_id']})
        if response_user_data.status_code == 200:
            request.session.update(response_user_data.json())
            return request
    return None



def home(request):
    # test
    data = {
        'photo': request.session['photo']
    }
    return render(request, 'service/home.html', data)



def register_page(request):
    if request.session.get('authenticated'):
        return redirect('home')
    
    if request.method == 'POST':

        data_to_api = {
            'username': request.POST['username'],
            'password1': request.POST['password1'],
            'password2': request.POST['password2'],
            'email': request.POST['email'],
        }

        response = requests.post(settings.REGISTER_API, data=data_to_api)
        if response.status_code == 201:
            request = login_support(request, request.POST['username'], request.POST['password1'])
            return redirect('home')
        
        form = forms.RegisterForm(data=request.POST)
        for k, v in response.json().items():
            try: form.add_error(k, v)
            except: form.add_error('password2', 'passwords not much')

        return render(request, 'service/register.html', {'form': form})

    elif request.method == 'GET':
        data = {
            'form': forms.RegisterForm
        }
        return render(request, 'service/register.html', data)
    


def login_page(request):
    if request.session.get('authenticated'):
        return redirect('home')

    if request.method == 'POST':
        result = login_support(request, request.POST['username'], request.POST['password'])
        if result:
            request = result
            return redirect('home')

        else:
            form = forms.LoginForm(data=request.POST)
            form.add_error('username', 'Wrong username or password!')
            return render(request, 'service/login.html', {'form': form})

    data = {
        'form': forms.LoginForm
    }
    return render(request, 'service/login.html', data)



def logout_page(request):
    request.session.flush()
    return redirect('home')