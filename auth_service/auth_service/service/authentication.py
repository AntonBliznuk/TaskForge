from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from . import models

class NoDBJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            return models.CustomUser(username='user', email='user_email@gmail.com', )
        except KeyError:
            raise InvalidToken("Missing user information in token")