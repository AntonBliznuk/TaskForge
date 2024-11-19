from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from . import models

class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.CustomUser
        fields = ('username', 'password1', 'password2', 'email')

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        new_user = models.CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            )
        new_user.set_password(validated_data['password1'])
        new_user.save()

        return new_user