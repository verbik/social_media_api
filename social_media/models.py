from django.db import models
from django.conf import settings


class Hashtag(models.Model):
    name = models.CharField()


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text_content = models.TextField()
    hashtags = models.ManyToManyField(Hashtag, blank=True)
