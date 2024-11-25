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

    # Group Service
    path('group/<int:group_id>/', views.group_page, name='grouppage'),
    path('create/group/', views.create_group_page, name='creategroup'),
    path('group/delete/<int:group_id>/', views.delete_group, name='deletegroup'),
    path('group/login/<int:group_id>/', views.login_group_page, name='logingroup'),
    path('group/logout/<int:group_id>/', views.logout_group_page, name='logoutgroup'),
    path('mygroups/', views.my_groups, name='mygroups'),

    # Task Service
    path('task/create/<int:group_id>/', views.create_task, name='taskcreate'),
    path('task/take/<int:task_id>/', views.take_task, name='tasktake'),
    path('task/inish/<int:task_id>/', views.finish_task, name='taskfinish'),

]
