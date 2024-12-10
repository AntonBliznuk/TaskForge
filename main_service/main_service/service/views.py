import jwt
import requests
import logging
from decouple import config
from functools import wraps

from . import forms

from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect


logger = logging.getLogger(__name__)

'''<--------------------------------------------------------------( Support Functions )-------------------------------------------------------------------------->'''


def login_support(request, username, password):
    """
    A function that authorizes users. The function sends a request with data to the authentication service and receives a token,
    then it decodes the token and receives user_id, then with the same token in the header and user_id in the body of the request,
    it sends a request for user data and writes it to the session.
    Accepts:
        request - request object,
        username - user name,
        password - user password.

    Returns a new request object with all entered data or None in case of failure.
    """
    # Send a request with the entered data.
    response = requests.post(settings.GET_TOKENS, data={'username': username, 'password': password,})

    # If the request is successful, write the token to the session and perform the following steps.
    if response.status_code == 200:
        request.session['access'] = response.json()['access']
        # Decode the received token.
        decoded = jwt.decode(response.json()['access'], config('SIGNING_KEY'), algorithms=config('ALGORITHM'))
        # Initialize the header dictionary with tokens to send a data request.
        headers = {"Authorization": f"Bearer {request.session.get('access')}"}

        # Send a request with all data and headers, if the request is successful, write the received information to the session. 
        response_user_data = requests.post(settings.GET_DATA_BY_ID, data={'user_id': decoded['user_id']}, headers=headers)
        if response_user_data.status_code == 200:
            request.session.update(response_user_data.json())
            # Return the modified request object.
            return request
        
    # If something went wrong, return None.
    return None



def login_required_view(func):
    """
    Decorator for session validation. If the user is not authorized,
    redirects to the login page.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('username'):
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper



def send_request_to_api(request, url, data_to_api, files={}):
    """
    Function for sending a request to API, in case of successful request returns a dictionary with the result,
    if the request was unsuccessful return None.
    Accepts:
        - request(Request object)
        - url(API link)
        - data_to_api(data to be passed in the request)
        - files(files that will be passed in the request)
    """
    headers = {"Authorization": f"Bearer {request.session.get('access')}"}
    response = requests.post(url, data=data_to_api, headers=headers, files=files)
    if response.status_code != 200:
        logger.info(f'{response.json()}')
        return None
    return response.json()

'''<--------------------------------------------------------------( Main Service )--------------------------------------------------------------------------------->'''

def home(request):
    """
    Function that displays the home page.
    """
    return render(request, 'service/home.html', {'request': request})

'''<--------------------------------------------------------------( Auth Service )-------------------------------------------------------------------------------->'''

@login_required_view
def user_profile_page(request, user_id):
    """
    Function for displaying the user's profile.
    Gets the id from the request and sends the request with a token in the header to get all user data.
    """
    response = send_request_to_api(request, settings.GET_DATA_BY_ID, {'user_id': user_id})
    if not response:
        return redirect('home')

    # Initialize the dictionary with all the necessary data.
    data = {
        'user': response,
        'groups_count': None,
        'completed_tasks_percentage': None,
        'date_joined': None,
        'request': request,
    }

    # Check if the user who sent the request is the owner of this account.
    if request.session.get('id') == response.get('id'):
        data['is_owner'] = True

    # Form a template based on the passed data and return it to the user.
    return render(request, 'service/profile.html', data)



@login_required_view
def change_profile_picture(request):
    """
    A feature that allows users to change their profile picture.
    Sends a request with a token in the header and all necessary data in the body of the request to the API.
    """
    if request.method != "POST":
        return redirect('home')
    
    # Retrieve the user's photo from the query.
    profile_picture = request.FILES.get("profile_picture")

    # Initialize the dictionary with files for photo transfer.
    files = {'profile_picture': (profile_picture.name, profile_picture.read(), profile_picture.content_type)}
    
    response = send_request_to_api(request, settings.CANGE_PHOTO_API, {'user_id': request.session.get('id')}, files=files)
    if not response:
        return redirect('home')

    # If the request is successful, redirect the user to their profile page.
    return redirect(reverse('profile', kwargs={'user_id': request.session.get('id')}))



def register_page(request):
    """
    Function for user registration in the auntification microservice.
    Immediately after registration, the function will authenticate the user.
    """
    # If the user is authenticated, we redirect them to the login page.
    if request.session.get('username'):
        return redirect('home')
    
    # If the request method is POST, perform the following actions.
    if request.method == 'POST':
        # Initialize the dictionary with all the necessary data to pass to the query.
        data_to_api = {
            'username': request.POST['username'],
            'password1': request.POST['password1'],
            'password2': request.POST['password2'],
            'email': request.POST['email'],
        }
        # Send the request, if everything is correct, perform the following actions.
        response = requests.post(settings.REGISTER_API, data=data_to_api)
        if response.status_code == 200:
            # Login the user and redirect to the home page.
            request = login_support(request, request.POST['username'], request.POST['password1'])
            return redirect('home')
        
        # If the registration was not successful, create a form and add all received errors to it.
        form = forms.RegisterForm(data=request.POST)
        for k, v in response.json().items():
            try: form.add_error(k, v)
            except: form.add_error('password2', 'passwords not much')

        # Pass the form to the template and return it to the user.
        return render(request, 'service/register.html', {'form': form})

    # If the request method is GET, pass an empty form to the template and return it to the user.
    elif request.method == 'GET':
        return render(request, 'service/register.html', {'form': forms.RegisterForm})
    


def login_page(request):
    """
    A feature that allows users to log in to an account.
    """
    # If the user is authenticated, we redirect them to the login page.
    if request.session.get('username'):
        return redirect('home')

    # If the request method is POST, perform the following actions.
    if request.method == 'POST':
        # Trying to log the user in.
        result = login_support(request, request.POST['username'], request.POST['password'])
        # If the user is logged in, we override the request object and redirect to the home page.
        if result:
            request = result
            return redirect('home')
        # If there are errors when logging in, create a form and add errors to it.
        # Then we pass the form with errors to the template that we return to the user.
        else:
            form = forms.LoginForm(data=request.POST)
            form.add_error('username', 'Wrong username or password!')
            return render(request, 'service/login.html', {'form': form})

    # If the request method not post, pass the form to the user.
    return render(request, 'service/login.html', {'form': forms.LoginForm})



def logout_page(request):
    """
    A feature that allows users to log out of an account.
    """
    # Completely clearing the session.
    request.session.flush()
    return redirect('home')

'''<--------------------------------------------------------------( Group Service )-------------------------------------------------------------------------------->'''

@login_required_view
def create_group_page(request):
    """
    A feature that allows users to create groups.
    """
    data = {
        'request': request,
        'form': forms.CreateGroupForm
    }
    if request.method == 'POST':
        # Create a dictionary with all the data from the request to pass it to the API.
        data_to_api = {
            "name": request.POST.get('name'),
            "password": request.POST.get('password'),
            "description": request.POST.get('description'),
            "creater_id": request.session.get('id')
        }
        response = send_request_to_api(request, settings.CREATE_GROUP_API, data_to_api)
        if response:
            return redirect(reverse('grouppage', kwargs={'group_id': response.get('group_id')}))
        
        # If the API request was unsuccessful, create a form and add an error to it.
        form = forms.CreateGroupForm()
        form.add_error('name', 'Someting went wrong!')
        data['form'] = form

    return render(request, 'service/create_group.html', data)



@login_required_view
def login_group_page(request, group_id):
    """
    A feature that allows users to join groups.
    """
    if request.method == 'POST':
        # Create a dictionary with all the data from the request to pass it to the API.
        data_to_api = {
            'password': request.POST.get('password'),
            'group_id': group_id
        }
        response = send_request_to_api(request, settings.ADD_USER_TO_GROUP, data_to_api)
        if response:
            return redirect(reverse('grouppage', kwargs={'group_id': group_id}))

    data = {
        'request': request,
        'form': forms.LogInGroupForm
    }
    return render(request, 'service/login_group.html', data)



@login_required_view
def group_page(request, group_id):
    """
    A feature that allows users to view group pages with all the necessary information.
    """
    if request.method != 'GET':
        return redirect('home')

    # Create a dictionary to which we will add all received data.
    data = {'request': request}

    # Get information about the group using API and add it to the dictionary.
    data_to_api = {'group_id': group_id}
    response = send_request_to_api(request, settings.GET_GROUP_INFO, data_to_api)
    if not response:
        return redirect(reverse('logingroup', kwargs={'group_id': group_id}))
    data['info'] = response.get('info')
    
    # We get information about users by means of the list of their id obtained from the first call, add the data to the dictionary.
    data_to_api = {'user_ids': response.get('members')}
    response = send_request_to_api(request, settings.INFO_BY_ID_LIST, data_to_api)
    if not response:
        return redirect('home')
    data['members'] = response.get('result')

    # Get task information using API, add data to the dictionary.
    data_to_api = {'group_id': group_id}
    response = send_request_to_api(request, settings.GROUP_TASK_LIST, data_to_api)
    if not response:
        return redirect('home')
    data['tasks'] = response.get('result')
    
    return render(request, 'service/group_page.html', data)



@login_required_view
def my_groups(request):
    """
    A feature that allows users to view all groups they have joined.
    """
    if request.method != 'GET':
        return redirect('home')
    data = {'request': request}

    response = send_request_to_api(request, settings.MY_GROUPS_API, {})
    if not response:
        return redirect('home')
    data['result'] = response.get('result')

    return render(request, 'service/my_groups.html', data)



@login_required_view
def logout_group_page(request, group_id):
    """
    A feature that allows users to quit groups.
    """
    if request.method != 'GET':
        return redirect('home')
    
    data_to_api = {'group_id': group_id}
    if not send_request_to_api(request, settings.DELETE_USER_FROM_GROUP, data_to_api):
        return redirect('home')
    return redirect('mygroups')



@login_required_view
def delete_group(request, group_id):
    """
    A function that allows the creator of a group to delete it.
    """
    if request.method != 'GET':
        return redirect('home')

    data_to_api = {'group_id': group_id}
    if not send_request_to_api(request, settings.DELETE_GROUP_API, data_to_api):
        return redirect('home')
    
    return redirect('mygroups')

'''<--------------------------------------------------------------( Task Service )-------------------------------------------------------------------------------->'''

@login_required_view
def create_task(request, group_id):
    """
    A feature that allows users to create tasks.
    """
    if request.method == 'POST':
        # Initialize dictionaries with data and files to pass them to the query.
        data_to_api = {
            'group_id': group_id,
            'title': request.POST.get('title'),
            'discription': request.POST.get('discription'),
        }
        photo = request.FILES.get("photo")
        files = {'photo': (photo.name, photo.read(), photo.content_type)}
        if not send_request_to_api(request, settings.CREATE_TASK_API, data_to_api, files):
            redirect('home')

        return redirect(reverse('grouppage', kwargs={'group_id': group_id}))

    data = {
        'request': request,
        'form': forms.CreateTaskForm
    }
    return render(request, 'service/create_task.html', data)



@login_required_view
def task_page(request, task_id):
    """
    A feature that allows users to view the task page with all the information about the task.
    """
    if request.method != 'GET':
        return redirect('home')

    data_to_api = {"task_id": task_id}
    response = send_request_to_api(request, settings.INFO_TASK_API, data_to_api)
    if not response:
        return redirect('home')

    data = {
        'task': response.get('result'),
        'request': request,
    }
    return render(request, 'service/task_page.html', data)



@login_required_view
def take_task(request, task_id):
    """
    A function that allows users to take a task to run, only one user can take a single task.
    """
    if request.method != 'GET':
        return redirect('home')
    
    data_to_api = {"task_id": task_id}
    if not send_request_to_api(request, settings.TAKE_TASK_API, data_to_api):
        return redirect('home')
    
    return redirect(reverse('taskpage', kwargs={'task_id': task_id}))



@login_required_view
def finish_task(request, task_id):
    """
    A function that allows users to finish a task.
    """
    if request.method != 'GET':
        return redirect('home')
    
    data_to_api = {"task_id": task_id}
    if not send_request_to_api(request, settings.FINISH_TASK_API, data_to_api):
        return redirect('home')
    
    return redirect(reverse('taskpage', kwargs={'task_id': task_id}))



@login_required_view
def delete_task(request, task_id):
    """
    A feature that allows users to delete a task after it has been completed.
    """
    if request.method != 'GET':
        return redirect('home')
    
    data_to_api = {"task_id": task_id}
    response = send_request_to_api(request, settings.DELETE_TASK_API, data_to_api)
    if not response:
        return redirect('home')
    
    return redirect(reverse('grouppage', kwargs={'group_id': response.get('group_id')}))