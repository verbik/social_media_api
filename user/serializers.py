from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as JwtTokenObtainPairSerializer,
)

from user.models import UserProfile


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        min_length=4, write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(UserProfileSerializer, self).validate(attrs=attrs)

        if self.instance is None:
            user = self.context["request"].user
            UserProfile.validate_unique_profile(user, ValidationError)

        return data

    class Meta:
        model = UserProfile
        fields = ("id", "user", "bio", "profile_picture", "followed_by")
        read_only_fields = (
            "user",
            "followed_by",
        )


class UserProfileListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")
    followers_amount = serializers.IntegerField()

    class Meta:
        model = UserProfile
        fields = ("id", "user", "bio", "profile_picture", "followers_amount")


class UserProfileDetailSerializer(UserProfileSerializer):
    user = serializers.CharField(source="user.username")
    followed_by = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )


class UserProfileFollowSerializer(serializers.ModelSerializer):
    follow = serializers.BooleanField()

    class Meta:
        model = UserProfile
        fields = ("follow",)
