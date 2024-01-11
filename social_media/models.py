import os.path
import uuid

from django.db import models
from django.conf import settings


class Hashtag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)

    filename = f"{instance.id}-{instance.user.id}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "post", filename)


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    image = models.ImageField(null=True, upload_to=post_image_file_path)
    text_content = models.TextField()
    hashtags = models.ManyToManyField(
        "Hashtag",
        blank=True,
        related_name="posts",
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="liked_posts"
    )
    comments = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Comment",
        related_name="commented_posts",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.user}. Posted {self.created_at}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    comment_contents = models.CharField(max_length=255)

    def __str__(self):
        return f"Comment by {self.user} posted {self.created_at}"
