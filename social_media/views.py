from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import PostFilter
from .serializers import PostSerializer, PostHashtagSerializer, PostListSerializer
from .models import Post


class LikeCommentMixin:
    pass


class AllPostsViewSet(viewsets.ModelViewSet, LikeCommentMixin):
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        user = self.request.user

        queryset = Post.objects.exclude(user=user)

        return queryset


class UserPostsViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        user = self.request.user

        queryset = Post.objects.filter(user=user)

        hashtag = self.request.query_params.get("#")
        if hashtag:
            queryset = queryset.filter(hashtags__name__icontains=hashtag)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "create":
            return PostHashtagSerializer

        return PostSerializer

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
