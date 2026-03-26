from django.conf import settings
from django.urls import include, re_path

from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.views.static import serve
from main import views as main_views
import drop.urls

urlpatterns = [
  re_path(r'^admin/', admin.site.urls),
  re_path(r'^auth/',include(auth_urls)),

  re_path(r'^$', main_views.home,name='home'),
  re_path(r'favicon.ico$', main_views.redirect,
      {'url': getattr(settings,'FAVICON','/static/favicon.png')}),
  re_path(r'',include(drop.urls)),
]

if settings.DEBUG:
  urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
  ]
