from django.db import models
from django.utils import timezone

from .models import Post


def get_optimized_queryset(
        manager=Post.objects, filters=True, annotations=False):
    queryset = manager.select_related('category', 'author', 'location')

    if filters:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if annotations:
        queryset = queryset.annotate(
            comment_count=models.Count('comments')
        ).order_by('-pub_date')

    return queryset
