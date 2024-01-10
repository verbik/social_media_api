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
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(UserProfileSerializer, self).validate(attrs=attrs)
        UserProfile.validate_profile(
            self.context["request"].user, attrs["followed_by"], ValidationError
        )
        return data

    class Meta:
        model = UserProfile
        fields = ("id", "user", "bio", "followed_by")
        read_only_fields = ("user",)

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        if user.profile is not None:
            raise ValidationError("This user already have an account!")
        return super().create(validated_data)


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


class UserProfileFollowSerializer(serializers.ModelSerializer):
    follow = serializers.BooleanField()

    class Meta:
        model = UserProfile
        fields = ("follow",)
