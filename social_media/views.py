from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import PostSerializer
from .models import Post


class LikeCommentView:
    pass


class AllPostsViewSet(viewsets.ModelViewSet, LikeCommentView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Post.objects.exclude(user=user)

        return queryset


class UserPostsViewSet(viewsets.ModelViewSet, LikeCommentView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Post.objects.filter(user=user)

        return queryset
