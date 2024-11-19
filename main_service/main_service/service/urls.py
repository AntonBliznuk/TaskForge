from django.urls import path
from .import views


urlpatterns = [ 
    # Info Pages
    path('', views.home, name='home'),

    # Auth Service
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('profile/<int:user_id>/', views.user_profile_page, name='profile'),
]
