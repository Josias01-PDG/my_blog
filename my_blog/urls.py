from django.contrib import admin
from django.urls import path, include, re_path
from blog.views import home, detail, videos, search, about, privacy, terms, category_detail, contact, subscribe
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('article/<int:article_id>/', detail, name='detail'),
    path('videos/', videos, name='videos'),

    path('search/', search, name='search'),
    path('a-propos/', about, name='about'),
    path('conditions/', terms, name='terms'),
    path('contact/', contact, name='contact'),
    path('confidentialite/', privacy, name='privacy'),
    path('newsletter/', subscribe, name='subscribe'),
    path('categorie/<int:category_id>/', category_detail, name='category'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]