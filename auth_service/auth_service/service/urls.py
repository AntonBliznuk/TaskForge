from django.urls import path
from .import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/databyid/', views.DataByUserId.as_view(), name='databyid'),
]
