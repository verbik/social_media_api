from django.db import transaction
from rest_framework import serializers

from .models import Hashtag, Post


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
            "text_content",
            "hashtags",
        )


class PostListSerializer(PostSerializer):
    hashtags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )


class PostHashtagSerializer(serializers.ModelSerializer):
    """Serializer for hashtag creation when creating a new post instance"""

    hashtags = HashtagSerializer(many=True, read_only=False, allow_empty=True)

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
