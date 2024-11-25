from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from . import serializers, models
import jwt
from decouple import config

'''<--------------------------------------------------------------( Support Functions )-------------------------------------------------------------------------->'''

def token_decode(token):
    decoded = jwt.decode(token, config('SIGNING_KEY'), algorithms=config('ALGORITHM'))
    if decoded.get('user_id'):
        return decoded
    return None


def verify_token(request):
    token = str(request.headers.get('Authorization')).split(' ')[1]
    if not token:
        return False

    token_result = token_decode(token)
    if not token_result:
        return False
    
    return token_result

'''<----------------------------------------------------------------( Endpoints )---------------------------------------------------------------------------------->'''

class CreareGroup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'})

        serializer = serializers.CreateGroupSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response({'message': 'succes', 'group_id':obj.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"add password from token"
class InfoGroup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'})
        
        group_id = request.data.get('group_id')
        group = models.Group.objects.filter(id=group_id).first()

        if not group:
            return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = serializers.GroupInfoSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)



class DeleteGroup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        
        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'})
        
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')

        group = models.Group.objects.filter(id=group_id).first()

        if not group:
            return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)

        if int(user_id) != int(group.creater_id):
            return Response({'message': 'you have to be the creater to delete group'}, status=status.HTTP_400_BAD_REQUEST)
        
        group.delete()
        return Response({'message': 'succes'}, status=status.HTTP_200_OK)



class AddUserToGroup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'})
        
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')
        password = request.data.get('password')

        group = models.Group.objects.filter(id=group_id).first()
        if not group:
            return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)
        role = models.Role.objects.filter(name='user').first()

        if group.password != password:
            return Response({'message': 'wrong password'}, status=status.HTTP_400_BAD_REQUEST)

        result = models.UserToGroup.objects.filter(user_id=user_id, group=group).first()
        if result:
            return Response({'message': 'user alredy in group'}, status=status.HTTP_200_OK)


        models.UserToGroup(
            user_id=user_id,
            role = role,
            group = group
        ).save()

        return Response({'message': 'succes'}, status=status.HTTP_200_OK)
        


class DeleteUserFromGroup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'})
        
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')

        group = models.Group.objects.filter(id=group_id).first() 
        user_to_group = models.UserToGroup.objects.filter(user_id=user_id, group=group).first()
        

        if not group:
            return Response({'message': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)

        if not user_to_group:
            return Response({'message': 'you don`t have premission'}, status=status.HTTP_400_BAD_REQUEST)

        models.UserToGroup.objects.filter(user_id=user_id, group=group).first().delete()
        return Response({'message': 'succes'}, status=status.HTTP_200_OK)


class UserGroups(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        result = verify_token(request)
        if not result:
            return Response({'message': 'no token or wrong one'})
        
        user_id = request.data.get('user_id')

        user_to_group = models.UserToGroup.objects.filter(user_id=user_id)
        if not user_to_group:
            return Response({'message': 'user not in groups'}, status=status.HTTP_204_NO_CONTENT)
        
        list_of_id = [i.group.id for i in user_to_group]

        return Response({'result': list_of_id}, status=status.HTTP_200_OK)

