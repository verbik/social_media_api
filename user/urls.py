from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from user.views import RegisterView, EmailTokenObtainPairView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register_user"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
]

app_name = "user"
