from django.urls import path
from . import views


urlpatterns = [
    path('api/mygroups/', views.UserGroups.as_view(), name='mygroups'),
    path('api/info/group/', views.InfoGroup.as_view(), name='info group'),
    path('api/group/userlist/', views.UserListGroup.as_view(), name='userlist'),
    path('api/create/group/', views.CreareGroup.as_view(), name='create group'),
    path('api/delete/group/', views.DeleteGroup.as_view(), name='adduser group'),
    path('api/adduser/group/', views.AddUserToGroup.as_view(), name='adduser group'),
    path('api/is/user/in/group/', views.IsUserInGroup.as_view(), name='isuseringroup'),
    path('api/deleteuser/group/', views.DeleteUserFromGroup.as_view(), name='delete group'),
]
