from django.db import transaction
from rest_framework import serializers

from .models import Hashtag, Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "username", "created_at", "comment_contents")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "comment_contents")

    def create(self, validated_data):
        user = self.context["request"].user

        comment = Comment.objects.create(user=user, **validated_data)

        return comment


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = (
            "id",
            "name",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "user",
            "image",
            "text_content",
            "hashtags",
            "likes",
            "comments",
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "image",
        )


class PostListSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    likes_amount = serializers.IntegerField()
    comments_amount = serializers.IntegerField()

    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "user",
            "image",
            "text_content",
            "hashtags",
            "likes_amount",
            "comments_amount",
        )


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(source="post_comments", many=True, read_only=True)
    likes = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="username"
    )


class PostLikeSerializer(serializers.ModelSerializer):
    like = serializers.BooleanField()

    class Meta:
        model = Post
        fields = ("like",)


class PostHashtagSerializer(serializers.ModelSerializer):
    """Serializer for hashtag creation when creating a new post instance"""

    hashtags = HashtagSerializer(
        many=True,
        read_only=False,
        allow_empty=True,
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "created_at",
            "text_content",
            "hashtags",
        )

    def create(self, validated_data):
        with transaction.atomic():
            hashtags_data = validated_data.pop("hashtags")
            post = Post.objects.create(**validated_data)
            if hashtags_data:
                hashtags = [
                    Hashtag.objects.get_or_create(name=tag["name"])[0]
                    for tag in hashtags_data
                ]
                post.hashtags.set(hashtags)
            return post


class PostUpdateSerializer(PostHashtagSerializer):
    hashtags = HashtagSerializer(many=True, read_only=False, allow_empty=True)

    class Meta:
        model = Post
        fields = (
            "text_content",
            "hashtags",
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            hashtags_data = validated_data.pop("hashtags", [])

            instance.text_content = validated_data.get(
                "text_content", instance.text_content
            )

            instance.save()

            if hashtags_data:
                hashtags = [
                    Hashtag.objects.get_or_create(name=tag["name"])[0]
                    for tag in hashtags_data
                ]
                instance.hashtags.set(hashtags)

        return instance
