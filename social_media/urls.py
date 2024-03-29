from rest_framework.routers import DefaultRouter

from social_media.views import AllPostsViewSet, UserPostsViewSet, CommentViewSet

router = DefaultRouter()
router.register("my-posts", UserPostsViewSet, basename="my-posts")
router.register("posts", AllPostsViewSet, basename="all-posts")
router.register("comments", CommentViewSet, basename="comments")

urlpatterns = router.urls

app_name = "social_media"
