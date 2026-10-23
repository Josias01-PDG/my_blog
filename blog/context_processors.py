from django.conf import settings

from .models import Category


def footer_categories(request):
    return {'footer_categories': Category.objects.order_by('name')}


def social_links(request):
    links = [
        link for link in settings.SOCIAL_LINKS
        if link.get('url', '').startswith(('https://', 'http://'))
    ]
    return {'social_links': links}