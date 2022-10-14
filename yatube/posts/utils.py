from django.core.paginator import Paginator
from django.conf import settings


def module_paginator(post_list, request):
    paginator = Paginator(post_list, settings.NUMB_PAGIN)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return context
