from django.urls import path
from .import views


urlpatterns = [ 
    # Main Service
    path('', views.home, name='home'),

    # Auth Service
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),
    path('profile/<int:user_id>/', views.user_profile_page, name='profile'),
    path('change/profile/picture', views.change_profile_picture, name='changephoto'),

    # Group Service
    path('mygroups/', views.my_groups, name='mygroups'),
    path('group/<int:group_id>/', views.group_page, name='grouppage'),
    path('create/group/', views.create_group_page, name='creategroup'),
    path('group/delete/<int:group_id>/', views.delete_group, name='deletegroup'),
    path('group/login/<int:group_id>/', views.login_group_page, name='logingroup'),
    path('group/logout/<int:group_id>/', views.logout_group_page, name='logoutgroup'),

    # Task Service
    path('task/<int:task_id>/', views.task_page, name='taskpage'),
    path('task/take/<int:task_id>/', views.take_task, name='tasktake'),
    path('task/finish/<int:task_id>/', views.finish_task, name='taskfinish'),
    path('task/delete/<int:task_id>/', views.delete_task, name='taskdelete'),
    path('task/create/<int:group_id>/', views.create_task, name='taskcreate'),

]
