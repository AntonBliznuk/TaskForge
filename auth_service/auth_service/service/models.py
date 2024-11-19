from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from decouple import config


class CustomUser(AbstractUser):
    """
    Model for storing user data.
    """
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    profile_picture = CloudinaryField('image', default=config('DEFAULT_USER_PHOTO_URL'))
    email = models.EmailField()

    def __str__(self):
        return f'{self.username} [{self.id}]'
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username', '-date_joined']