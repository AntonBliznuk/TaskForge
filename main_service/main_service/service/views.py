import jwt
import requests
from decouple import config

from . import forms

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse


'''<--------------------------------------------------------------( Support Functions )-------------------------------------------------------------------------->'''


def login_support(request, username, password):
    data_to_api = {
        'username': username,
        'password': password,
    }
    response = requests.post(settings.GET_TOKENS, data=data_to_api)
    if response.status_code == 200:
        request.session['access'] = response.json()['access']
        decoded = jwt.decode(response.json()['access'], config('SIGNING_KEY'), algorithms=config('ALGORITHM'))

        headers = {
        "Authorization": f"Bearer {request.session.get('access')}"
        }
        response_user_data = requests.post(settings.GET_DATA_BY_ID, data={'user_id': decoded['user_id']}, headers=headers)
        if response_user_data.status_code == 200:
            request.session.update(response_user_data.json())
            return request
    return None


'''<--------------------------------------------------------------( Main Service )--------------------------------------------------------------------------------->'''


def home(request):
    data = {
        'request': request,
        'is_authenticated': request.session.get('authenticated')
    }
    return render(request, 'service/home.html', data)


'''<--------------------------------------------------------------( Auth Service )-------------------------------------------------------------------------------->'''


def user_profile_page(request, user_id):
    if not request.session.get('authenticated'):
        return redirect('login')
    
    headers = {
        "Authorization": f"Bearer {request.session.get('access')}"
        }
    response_user_data = requests.post(settings.GET_DATA_BY_ID, data={'user_id': user_id}, headers=headers)
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


def create_group_page(request):

    if not request.session.get('authenticated'):
        return redirect('login')
    
    data = {
        'request': request,
        'is_authenticated': request.session.get('authenticated'),
        'form': forms.CreateGroupForm
    }
    
    if request.method == 'POST':
    
        data = {
            "name": request.POST.get('name'),
            "password": request.POST.get('password'),
            "description": request.POST.get('description'),
            "creater_id": request.session.get('id')
        }
        headers = {
            "Authorization": f"Bearer {request.session.get('access')}"
        }
        response = requests.post(settings.CREATE_GROUP_API, data=data, headers=headers)
        if response.status_code == 201:
            group_id = int(response.json().get('group_id'))

            headers = {
            "Authorization": f"Bearer {request.session.get('access')}"
            }
            data_to_api = {
                'password': request.POST.get('password'),
                'user_id': request.session.get('id'),
                'group_id': group_id
            }
            response = requests.post(settings.ADD_USER_TO_GROUP, data=data_to_api, headers=headers)
            if response.status_code == 200:
                return redirect('home')
        
        form = forms.CreateGroupForm(data=requests.POST)
        form.add_error('name', 'Someting went wrong!')

        data['form'] = form

    return render(request, 'service/create_group.html', data)



def login_group_page(request, group_id):

    if not request.session.get('authenticated'):
        return redirect('login')
    
    data = {
        'request': request,
        'is_authenticated': request.session.get('authenticated'),
        'form': forms.LogInGroupForm
    }

    if request.method == 'POST':
        
        headers = {
            "Authorization": f"Bearer {request.session.get('access')}"
        }
        data_to_api = {
            'password': request.POST.get('password'),
            'user_id': request.session.get('id'),
            'group_id': group_id
        }
        response = requests.post(settings.ADD_USER_TO_GROUP, data=data_to_api, headers=headers)
        print(response.json())


    return render(request, 'service/login_group.html', data)



def group_page(request, group_id):
    if not request.session.get('authenticated'):
        return redirect('login')

    if request.method != 'GET':
        return redirect('home')

    data = {
        'request': request,
        'is_authenticated': request.session.get('authenticated'),
    }

    headers = {
        "Authorization": f"Bearer {request.session.get('access')}"
    }
    data_to_api = {
        'group_id': group_id
    }
    response = requests.post(settings.GET_GROUP_INFO, data=data_to_api, headers=headers)
    if response.status_code == 200:
        data['info'] = response.json()

    else:
        return redirect(reverse('logingroup', kwargs={'group_id': group_id}))
    
    return render(request, 'service/group_page.html', data)



def my_groups(request):
    if not request.session.get('authenticated'):
        return redirect('login')

    if request.method != 'GET':
        return redirect('home')
    
    data = {
        'request': request,
        'is_authenticated': request.session.get('authenticated'),
    }
    headers = {
        "Authorization": f"Bearer {request.session.get('access')}"
    }
    data_to_api = {
        'user_id': request.session.get('id'),
    }

    response = requests.post(settings.MY_GROUPS_API, data=data_to_api, headers=headers)
    if response.status_code == 200:
        id_list = response.json().get('result')
        groups = []

        for id in id_list:
            response = requests.post(settings.GET_GROUP_INFO, data={'group_id': id}, headers=headers)
            if response.status_code == 200:
                groups.append(response.json())
                
        data['result'] = groups
    
    elif response.status_code == 204:
        data['result'] = 'no groups'

    else:
        return redirect('home')

    return render(request, 'service/my_groups.html', data)



def logout_group_page(request, group_id):

    if not request.session.get('authenticated'):
        return redirect('login')
    
    if request.method != 'GET':
        return redirect('home')
    
    headers = {
        "Authorization": f"Bearer {request.session.get('access')}"
    }
    data = {
        'user_id': request.session.get('id'),
        'group_id': group_id
    }
    resoponse = requests.post(settings.DELETE_USER_FROM_GROUP, headers=headers, data=data)
    print(resoponse.json())
    return redirect('home')



def delete_group(request, group_id):

    if not request.session.get('authenticated'):
        return redirect('login')
    
    if request.method != 'GET':
        return redirect('home')

    headers = {
        "Authorization": f"Bearer {request.session.get('access')}"
    }
    data = {
        'user_id': request.session.get('id'),
        'group_id': group_id
    }

    response = requests.post(settings.DELETE_GROUP_API, data=data, headers=headers)
    if response.status_code != 200:
        print(response.json())
    return redirect('home')
    


'''<--------------------------------------------------------------( Task Srvice )-------------------------------------------------------------------------------->'''

def create_task(request, group_id):
    pass

def take_task(request, task_id):
    pass

def finish_task(request, task_id):
    pass