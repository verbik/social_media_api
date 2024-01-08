from django.contrib import admin

from social_media.models import Hashtag, Post, Comment

admin.site.register(Hashtag)
admin.site.register(Post)
admin.site.register(Comment)
