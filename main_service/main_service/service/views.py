import jwt
import requests
from decouple import config

from . import forms

from django.conf import settings
from django.shortcuts import render, redirect


'''<--------------------------------------------------------------( Support Functions )-------------------------------------------------------------------------->'''


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


'''<--------------------------------------------------------------( Info Pages )---------------------------------------------------------------------------------->'''


def home(request):
    # print(request.session.get('user_id'))
    # test
    data = {
        'request': request,
        'is_authenticated': request.session.get('authenticated')
    }
    return render(request, 'service/home.html', data)


'''<--------------------------------------------------------------( Auth Service )-------------------------------------------------------------------------------->'''


def user_profile_page(request, user_id):
    if not request.session.get('authenticated'):
        return redirect('login')
    
    response_user_data = requests.post(settings.GET_DATA_BY_ID, data={'user_id': user_id})
    if response_user_data.status_code == 200:
        response_user_data = response_user_data.json()
        data = {
            'username': response_user_data['username'],
            'photo': response_user_data['photo'],
            'groups_count': None,
            'completed_tasks_percentage': None,
            'date_joined': None,
            'request': request,
            'is_authenticated': request.session.get('authenticated')
        }
        if request.session.get('id') == response_user_data['id']:
            data['is_owner'] = True

        return render(request, 'service/profile.html', data)



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


'''<--------------------------------------------------------------( Group Srvice )-------------------------------------------------------------------------------->'''