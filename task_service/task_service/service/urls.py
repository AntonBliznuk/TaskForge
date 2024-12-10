from django.urls import path
from . import views


urlpatterns = [
    path('api/task/info/', views.InfoTask.as_view(), name='taskinfo'),
    path('api/task/take/', views.TakeTaskAPI.as_view(), name='taketask'),
    path('api/group/tasks/', views.GroupTasks.as_view(), name='grouptasks'),
    path('api/create/task/', views.CreateTaskAPI.as_view(), name='createtask'),
    path('api/task/finish/', views.FinishTaskAPI.as_view(), name='finishtask'),
    path('api/task/delete/', views.DeleteTaskAPI.as_view(), name='deletetask'),
]