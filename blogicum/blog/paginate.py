from django.core.paginator import Paginator
from django.conf import settings


def get_paginator(request, queryset, per_page=settings.NUM_OF_POSTS):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {'page_obj': page_obj}
