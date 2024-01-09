from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserSerializer, TokenObtainPairSerializer


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            return Response(status=status.HTTP_201_CREATED)
        return response


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_200_OK)
        except TokenError as e:
            return Response(
                {"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST
            )
        except KeyError:
            return Response(
                {"detail": "'refresh_token' not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": "An error occurred during logout."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
