import jwt
from decouple import config
from functools import wraps

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



def is_user_in_group(user_id, group):
    """
    The function determines whether the user is a member of the group,
    if no, it returns False, if yes, it returns True.
    Accepts:
        - user_id (unique user number)
        - group (group object)
    """
    # Check for cache.
    cache_key = f'{user_id}_is_in_group_{group.id}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    result = models.UserToGroup.objects.filter(user_id=user_id, group=group).exists()
    cache.set(cache_key, result, timeout=3600)
    return result



ROLE_USER = models.Role.objects.get(name='user')
def get_user_role():
    """
    Returns a “user” role object using a global variable for caching.
    """
    global ROLE_USER
    if ROLE_USER is None:
        ROLE_USER, _ = models.Role.objects.get_or_create(name='user')
    return ROLE_USER

'''<----------------------------------------------------------------( Endpoints )---------------------------------------------------------------------------------->'''

class CreareGroup(APIView):
    """
    Endpoint for creating groups.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        # Pass all received data from POST request to serializer,
        # if everything is correct, save the new object and return the response to the client. 
        serializer = serializers.CreateGroupSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            models.UserToGroup(
                user_id=request.user_data.get('user_id'),
                role = get_user_role(),
                group = obj
            ).save()

            return Response({'message': 'succes', 'group_id':obj.id}, status=status.HTTP_200_OK)
        
        # If something went wrong, return a response to the user with all the errors.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class InfoGroup(APIView):
    """
    Endpoint to get information about the group.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{group_id}_group_info'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Get the group id from the query and search for a group with the same id,
        # if such a group does not exist, return the corresponding response.
        try: group = models.Group.objects.get(id=request.data.get('group_id'))
        except: return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)

        # We get the user id from the token and find out if this user is a member of the group found,
        # if not we return the corresponding answer.
        if not is_user_in_group(user_id=request.user_data.get('user_id'), group=group):
            return Response({'message': 'you are not in group'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.GroupInfoSerializer(group)
        users_ids = models.UserToGroup.objects.filter(group_id=request.data.get('group_id')).values_list('user_id', flat=True)
        data = {'info': serializer.data, 'members': list(users_ids)}

        cache.set(cache_key, data, timeout=3600)
        return Response(data, status=status.HTTP_200_OK)



class DeleteGroup(APIView):
    """
    Endpoint for deleting a group.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        cache_key = f'{group_id}_group_info'
        cache.delete(cache_key)

        # Get the group id from the query and search for a group with the same id,
        # if such a group does not exist, return the corresponding response.
        try: group = models.Group.objects.get(id=request.data.get('group_id'))
        except: return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # We get the user id from the token.
        user_id = request.user_data.get('user_id')

        # Check if the user is the creator of the group, if not, return the corresponding answer.
        if int(user_id) != int(group.creater_id):
            return Response({'message': 'you have to be the creater to delete group'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If all went well, we delete the object, returns a response to the user.
        group.delete()
        return Response(status=status.HTTP_200_OK)



class AddUserToGroup(APIView):
    """
    Endpoint that will allow users to join groups.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the group id from the query and search for a group with the same id,
        # if such a group does not exist, return the corresponding response.
        try: group = models.Group.objects.get(id=request.data.get('group_id'))
        except: return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check the correctness of the entered password.
        password = request.data.get('password')
        if group.password != password:
            return Response({'message': 'wrong password'}, status=status.HTTP_400_BAD_REQUEST)

        # We get the user id from the token and find out if this user is a member of the group found,
        # if this user is a member of the group we return the corresponding answer.
        user_id = request.user_data.get('user_id')
        if is_user_in_group(user_id=user_id, group=group):
            return Response({'message': 'you are not in group'}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the group.
        models.UserToGroup(
            user_id=user_id,
            role = get_user_role(),
            group = group
        ).save()

        cache_key = f'{user_id}_is_in_group_{group.id}'
        cache.delete(cache_key)

        cache_key = f'{group_id}_group_info'
        cache.delete(cache_key)

        # Sending a response to the client.
        return Response({'message': 'success'},status=status.HTTP_200_OK)
        


class DeleteUserFromGroup(APIView):
    """
    Endpoint that allows users to leave the group.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the group id from the query and search for a group with the same id,
        # if such a group does not exist, return the corresponding response.
        try: group = models.Group.objects.get(id=request.data.get('group_id'))
        except: return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)

        # We get the user id from the token and find out if this user is a member of the group found,
        # if this user isn't a member of the group we return the corresponding answer.
        user_id = request.user_data.get('user_id')
        try: user_to_group = models.UserToGroup.objects.get(user_id=user_id, group=group)
        except: return Response({'message': 'you are not in group'}, status=status.HTTP_400_BAD_REQUEST)

        # If all went well, we delete the object, returns a response to the user.
        cache_key = f'{user_id}_is_in_group_{group.id}'
        cache.delete(cache_key)
        cache_key = f'{group_id}_group_info'
        cache.delete(cache_key)

        user_to_group.delete()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)



class UserGroups(APIView):
    """
    Endpoint that allows to get the list of id of all groups a user is a member of.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):
        user_id = request.user_data.get('user_id')
        if not user_id:
            return Response({'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{user_id}_groups'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'result': cached_data}, status=status.HTTP_200_OK)
        
        # Get the id's of all groups and return them to the client.
        groups = models.Group.objects.filter(id__in=models.UserToGroup.objects.filter(user_id=user_id).values_list('group', flat=True))
        serialized_data = serializers.GroupInfoSerializer(groups, many=True).data

        cache.set(cache_key, serialized_data, timeout=3600)
        return Response({'result': serialized_data, 'amount': len(list(groups))}, status=status.HTTP_200_OK)



class UserListGroup(APIView):
    """
    Endpoint that allows you to get the id of all users who are members of a certain group.
    """
    permission_classes = [AllowAny]

    @token_required
    def post(self, request):
        group_id = request.user_data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{group_id}_group_user_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'result': cached_data}, status=status.HTTP_200_OK)

        # Get the group id from the query and search for a group with the same id,
        # if such a group does not exist, return the corresponding response.
        if not models.Group.objects.filter(id=group_id).exists():
            return Response({'message': 'wrong group id'}, status=status.HTTP_400_BAD_REQUEST)

        # Get all users in the group, write their id's to the list and return them to the client.
        users_ids = models.UserToGroup.objects.filter(group_id=request.data.get('group_id')).values_list('user_id', flat=True)

        cache.set(cache_key, users_ids, timeout=3600)
        return Response({'result': users_ids}, status=status.HTTP_200_OK)



class IsUserInGroup(APIView):

    permission_classes = [AllowAny]

    @token_required
    def post(self, request):

        group_id = request.data.get('group_id')
        if not group_id:
            return Response({'message': 'group_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user_data.get('user_id')
        if not user_id:
            return Response({'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{user_id}_is_in_group_{group_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(status=status.HTTP_200_OK)

        # Get the group id from the query and search for a group with the same id,
        # if such a group does not exist, return the corresponding response.
        try: group = models.Group.objects.get(id=request.data.get('group_id'))
        except: return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)

        # We get the user id from the token and find out if this user is a member of the group found,
        # if this user isn't a member of any groups we return the corresponding answer.
        user_id = request.user_data.get('user_id')
        if not is_user_in_group(user_id=user_id, group=group):
            return Response({'message': 'you are not in group'}, status=status.HTTP_400_BAD_REQUEST)

        cache.set(cache_key, True, timeout=3600)

        # Sending a response to the client.
        return Response({'message': 'success'}, status=status.HTTP_200_OK) 
