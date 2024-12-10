from . import serializers, models
from django.core.cache import cache 

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny



class RegisterAPIView(APIView):
    """
    Endpoint for user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Pass all received data from POST request to serializer,
        # if everything is correct, save the new object and return the response to the client. 
        serializer = serializers.RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'succes'}, status=status.HTTP_200_OK)
        
        # If something went wrong, return a response to the user with all the errors.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class DataByUserId(APIView):
    """
    Endpoint to get information about a user by user ID.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get user_id from the query and search for user by this id.
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{user_id}_data_by_id'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try: user = models.CustomUser.objects.get(id=user_id)
        except: return Response({'message': 'unknown user id'}, status=status.HTTP_400_BAD_REQUEST)

        serialized_data = serializers.InfoUserSerializer(user).data
        cache.set(cache_key, serialized_data, timeout=3600)

        # If the user was found, return the data to the client.
        return Response(serialized_data, status=status.HTTP_200_OK)



class CangeUserPhoto(APIView):
    """
    Endpoint for changing user's photo.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get user_id from the query and search for user by this id.
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'message': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'{user_id}_data_by_id'
        cache.delete(cache_key)

        try: user = models.CustomUser.objects.get(id=user_id)
        except: return Response({'message': 'unknown user id'}, status=status.HTTP_400_BAD_REQUEST)

        # If the user with such user_id does not exist, we return the corresponding message.
        if not user:
            return Response({'message': 'unknown user id'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Saving a photo from a user request.
        user.profile_picture = request.data.get('profile_picture')
        user.save()

        # Return a message to the client that the photo has been successfully changed.
        return Response({'message': 'succes'}, status=status.HTTP_200_OK)



class UserIdBYIdList(APIView):
    """
    Endpoint to retrieve user information by list.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get user_ids from the query.
        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({'message': 'user_ids is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for cache.
        cache_key = f'{sorted(user_ids)}_data_by_id_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({"result": cached_data}, status=status.HTTP_200_OK)

        # Looking for users, serializing the data, returning a response to the client.
        users = models.CustomUser.objects.filter(id__in=user_ids)
        serialized_data = serializers.InfoUserSerializer(users, many=True).data

        cache.set(cache_key, serialized_data, timeout=3600)
        return Response({"result": serialized_data}, status=status.HTTP_200_OK)
    