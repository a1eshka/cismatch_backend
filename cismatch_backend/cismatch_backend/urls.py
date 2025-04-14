from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('post.urls')),
    path('api/teams/', include('team.urls')),
    path('api/servers/', include('server.urls')),
    path('api/adverts/', include('advert.urls')),
    path('api/auth/', include('useraccount.urls')),
    path('api/raffles/', include('raffle.urls')),
    path('api/grenade/', include('grenade.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
