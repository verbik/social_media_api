from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as JwtTokenObtainPairSerializer,
)

from user.models import UserProfile


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "user", "bio", "followed_by")


class UserProfileListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")
    followers_amount = serializers.IntegerField()

    class Meta:
        model = UserProfile
        fields = ("id", "user", "bio", "followers_amount")


class UserProfileDetailSerializer(UserProfileSerializer):
    user = serializers.CharField(source="user.username")
    followed_by = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )
