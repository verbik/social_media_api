from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from user.views import (
    RegisterView,
    EmailTokenObtainPairView,
    LogoutView,
    AllUsersProfileViewSet,
)

router = DefaultRouter()
router.register("profiles", AllUsersProfileViewSet)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register_user"),
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
    path("", include(router.urls)),
]

app_name = "user"
