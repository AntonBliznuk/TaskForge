import jwt
import requests
from decouple import config
from functools import wraps

from django.conf import settings
from django.core.cache import cache 

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from . import serializers, models

'''<--------------------------------------------------------------( Support Functions )-------------------------------------------------------------------------->'''

def token_decode(token):
    """
    The function to decode the token, if the decoding was successful,
    returns a dictionary with decoded data, and in case of failure None.
    Accepts:
        - token (acces token from request)
    """
    # Decoding a token using environment variables.
    decoded = jwt.decode(token, config('SIGNING_KEY'), algorithms=config('ALGORITHM'))

    # If it was possible to get the data from the token, return it.
    if decoded.get('user_id'):
        return decoded
    
    # If it was not possible to get data from the token, return None.
    return None



def verify_token(request):
    """
    The user verification function, gets the token from the request,
    decodes it and if all goes well returns the decoded data.
    Accepts:
        - request (request object from user)
    """
    # Get the token from the request header and if there is no token, return False.
    token = str(request.headers.get('Authorization')).split(' ')[1]
    if not token:
        return False

    # Try to decode the token and if it fails, return False.
    token_result = token_decode(token)
    if not token_result:
        return False
    
    # If everything was successful, return the result of decoding.
    return token_result



def token_required(view_func):
    """
    The decorator that ensures the view requires a valid token for access.
    """
    @wraps(view_func)
    def wrapped_view(self, request, *args, **kwargs):
        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'}, status=status.HTTP_401_UNAUTHORIZED)
        request.user_data = result
        return view_func(self, request, *args, **kwargs)
    return wrapped_view



def is_in_group(request, group_id):
    """
    Function for checking whether a user is a member of a group.
    Accepts:
        - request (request object)
        - group_id (Unique group number)
    """
    headers={"Authorization": f"Bearer {request.headers.get('Authorization').split(' ')[1]}"}
    response = requests.post(settings.IS_USER_IN_GROUP_API, data={'group_id': group_id}, headers=headers)
    if response.status_code != 200:
        return False
    return True


'''<----------------------------------------------------------------( Endpoints )---------------------------------------------------------------------------------->'''

class CreateTaskAPI(APIView):
    """
    Endpoint for creating a new task.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        # Checking the user for group membership.
        group_id = request.data.get('group_id')
        if not is_in_group(request, group_id):
            return Response({'message': 'you are not in group'}, status=status.HTTP_403_FORBIDDEN)

        cache_key = f'{group_id}_task_list'
        cache.delete(cache_key)

        # Creating a new object.
        models.Task(
            group_id=group_id,
            title=request.data.get('title'),
            discription=request.data.get('discription'),
            photo=request.data.get('photo')
        ).save()

        return Response({'message': 'success'}, status=status.HTTP_200_OK)



class GroupTasks(APIView):
    """
    Endpoint to retrieve all tasks of a group.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{group_id}_task_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'result': cached_data}, status=status.HTTP_200_OK)

        # Checking the user for group membership.
        if not is_in_group(request, group_id):
            return Response({'message': 'you are not in group'}, status=status.HTTP_403_FORBIDDEN)

        # Receiving all group tasks.
        tasks = models.Task.objects.filter(group_id=group_id)
        serialized_data = serializers.TaskSerializer(tasks, many=True).data

        cache.set(cache_key, serialized_data, timeout=3600)
        return Response({'result': serialized_data}, status=status.HTTP_200_OK)



class InfoTask(APIView):
    """
    Endpoint for getting information and tasks.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'message': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{task_id}_task_info'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'result': cached_data}, status=status.HTTP_200_OK)
        
        # Obtaining a task object.
        try: task = models.Task.objects.get(id=task_id)
        except: return Response({'message': 'wrong task id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking the user for group membership.
        if not is_in_group(request, task.group_id):
            return Response({'message': 'you are not in group'}, status=status.HTTP_403_FORBIDDEN)
        
        serialized_data = serializers.TaskSerializer(task).data
        cache.set(cache_key, serialized_data, timeout=3600)
        return Response({'result': serialized_data}, status=status.HTTP_200_OK)



class TakeTaskAPI(APIView):
    """
    Endpoint that allows users to take tasks.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'message': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'{task_id}_task_info'
        cache.delete(cache_key)

        # Obtaining a task object.
        try: task = models.Task.objects.get(id=task_id)
        except: return Response({'message': 'wrong task id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking the user for group membership.
        if not is_in_group(request, task.group_id):
            return Response({'message': 'you are not in group'}, status=status.HTTP_403_FORBIDDEN)
    
        task.take(user_id=int(request.user_data.get('user_id')))
        task.save()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)



class FinishTaskAPI(APIView):
    """
    Endpoint that allows users to finish tasks.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'message': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'{task_id}_task_info'
        cache.delete(cache_key)

        # Obtaining a task object.
        try: task = models.Task.objects.get(id=task_id)
        except: return Response({'message': 'wrong task id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking the user for group membership.
        if not is_in_group(request, task.group_id):
            return Response({'message': 'you are not in group'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has the right to finish the task.
        if task.user_id != request.user_data.get('user_id'):
            return Response({'message': 'This is not your task'}, status=status.HTTP_400_BAD_REQUEST)

        task.finish()
        task.save()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)
        


class DeleteTaskAPI(APIView):
    """
    Endpoint that allows users to delete tasks.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'message': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtaining a task object.
        try: task = models.Task.objects.get(id=task_id)
        except: return Response({'message': 'wrong task id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Checking the user for group membership.
        if not is_in_group(request, task.group_id):
            return Response({'message': 'you are not in group'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has the right to finish the task.
        if task.user_id != request.user_data.get('user_id'):
            return Response({'message': 'This is not your task'}, status=status.HTTP_400_BAD_REQUEST)

        task.delete()
        cache_key = f'{task.group_id}_task_list'
        cache.delete(cache_key)

        cache_key = f'{task_id}_task_info'
        cache.delete(cache_key)
        return Response({'group_id': task.group_id}, status=status.HTTP_200_OK)