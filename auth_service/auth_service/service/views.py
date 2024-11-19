from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
from . import serializers, models

class RegisterAPIView(APIView):
    
    def post(self, request):
        
        serializer = serializers.RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'succes'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DataByUserId(APIView):

    def post(self, request):
        user_id = request.POST['user_id']
        user = models.CustomUser.objects.filter(id=user_id).first()
        if user:
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'photo': user.profile_picture.url,
                'authenticated': True,
                }, status=status.HTTP_200_OK)
        
        else:
            return Response({'message': 'unknown user id'}, status=status.HTTP_400_BAD_REQUEST)

