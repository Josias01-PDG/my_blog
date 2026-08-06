from django.contrib import admin
from django.urls import path, include, re_path
from blog.views import home, detail
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('article/<int:article_id>/', detail, name='detail'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

