from django.db import models
from django.conf import settings


class Hashtag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text_content = models.TextField()
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    comments = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, through="Comments"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.user}. Posted {self.created_at}"


class Comments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=255)
