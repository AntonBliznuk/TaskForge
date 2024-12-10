from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoinds for user management.
    path('api/register/', views.RegisterAPIView.as_view(), name='register'),
    path('api/databyid/', views.DataByUserId.as_view(), name='databyid'),
    path('api/change/photo/', views.CangeUserPhoto.as_view(), name='changephoto'),
    path('api/infoidlist/', views.UserIdBYIdList.as_view(), name='infoiflist'),
]
