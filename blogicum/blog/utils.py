from django.db import models
from django.core.paginator import Paginator
from django.utils import timezone

from blogicum.settings import NUM_OF_POSTS
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


def get_paginator(request, queryset, per_page=NUM_OF_POSTS):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {'page_obj': page_obj}
