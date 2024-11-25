from django.urls import path
from . import views


urlpatterns = [
    path('api/info/group/', views.InfoGroup.as_view(), name='info group'),
    path('api/create/group/', views.CreareGroup.as_view(), name='create group'),
    path('api/delete/group/', views.DeleteGroup.as_view(), name='adduser group'),
    path('api/adduser/group/', views.AddUserToGroup.as_view(), name='adduser group'),
    path('api/deleteuser/group/', views.DeleteUserFromGroup.as_view(), name='delete group'),
    path('api/mygroups/', views.UserGroups.as_view(), name='mygroups'),
]
