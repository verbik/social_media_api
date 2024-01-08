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
