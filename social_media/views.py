from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from .filters import PostFilter
from .serializers import (
    PostSerializer,
    PostHashtagSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
)
from .models import Post, Comment


class LikeCommentMixin:
    pass


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class AllPostsViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, LikeCommentMixin, GenericViewSet
):
    serializer_class = PostListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Post.objects.exclude(user=user)
            .prefetch_related("hashtags")
            .annotate(likes_amount=Count("likes"), comments_amount=Count("comments"))
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        return PostSerializer


class UserPostsViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = PostFilter

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Post.objects.filter(user=user)
            .prefetch_related("hashtags")
            .annotate(likes_amount=Count("likes"), comments_amount=Count("comments"))
        )

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
