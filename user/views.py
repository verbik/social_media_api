from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets, permissions
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import UserProfileFilter
from .models import UserProfile
from .serializers import (
    UserSerializer,
    TokenObtainPairSerializer,
    UserProfileSerializer,
    UserProfileListSerializer,
    UserProfileDetailSerializer,
    UserProfileFollowSerializer,
)


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
        """Endpoint for logging out and making token invalid"""
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


class AllUsersProfileViewSet(
    GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserProfileFilter

    def get_queryset(self):
        user = self.request.user

        queryset = UserProfile.objects.exclude(user=user).prefetch_related("user")

        if self.action == "list":
            queryset = queryset.annotate(followers_amount=Count("followed_by"))

        username = self.request.query_params.get("")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer

        if self.action == "retrieve":
            return UserProfileDetailSerializer

        if self.action == "follow_user":
            return UserProfileFollowSerializer

        return UserProfileSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow-user",
        permission_classes=[IsAuthenticated],
    )
    def follow_user(self, request: Request, pk=None) -> Response:
        """Endpoint for following specified user"""
        user_profile = self.get_object()
        user = self.request.user

        if user in user_profile.followed_by.all():
            user_profile.followed_by.remove(user)
        else:
            user_profile.followed_by.add(user)

        user_profile.refresh_from_db()

        return Response(status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="following",
        permission_classes=[IsAuthenticated],
    )
    def following(self, request: Request) -> Response:
        """Endpoint to see profiles active user is following"""
        user = self.request.user

        followed_profiles = UserProfile.objects.filter(followed_by=user)

        serializer = UserProfileDetailSerializer(followed_profiles, many=True)

        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type={"type": "str"},
                description="Filter profiles by username(ex. ?username=username)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class MyUserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = UserProfile.objects.filter(user=self.request.user)
        return queryset

    @action(
        methods=["GET"],
        detail=False,
        url_path="followers",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def follower_list(self, request):
        """Endpoint to get list of users who follows request.user profile"""
        user_profile = UserProfile.objects.get(user=request.user)

        followers = user_profile.followed_by.all()

        serializer = UserSerializer(followers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
