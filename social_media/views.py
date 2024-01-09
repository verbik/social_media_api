from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .filters import PostFilter
from .serializers import (
    PostSerializer,
    PostHashtagSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    PostLikeSerializer,
)
from .models import Post, Comment


class LikeCommentMixin(GenericViewSet):
    @action(
        methods=["POST"],
        detail=True,
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def comments(self, request: Request, pk=None) -> Response:
        """Endpoint for posting a comment to specified post"""
        post = self.get_object()
        comment_contents = request.data.get("comment_contents")

        comment = Comment.objects.create(
            user=request.user,
            post=post,
            comment_contents=comment_contents,
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
        permission_classes=[IsAuthenticated],
    )
    def like(self, request: Request, pk=None) -> Response:
        """Endpoint for liking a specified post"""
        post = self.get_object()
        user = self.request.user

        if user in post.likes.all():
            post.likes.remove(user)
        else:
            post.likes.add(user)

        post.refresh_from_db()

        return Response(status=status.HTTP_200_OK)


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

        if self.action == "comments":
            return CommentCreateSerializer

        if self.action == "like":
            return PostLikeSerializer

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

        if self.action == "retrieve":
            return PostDetailSerializer

        return PostSerializer

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
