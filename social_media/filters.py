import django_filters
from .models import Post


class PostFilter(django_filters.FilterSet):
    hashtags = django_filters.CharFilter(
        field_name="hashtags__name", lookup_expr="icontains"
    )

    class Meta:
        model = Post
        fields = ["hashtags"]
