from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('articles.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('articles.api_urls')),
    path('analytics/', include('analytics.urls')),
    path('recommendations/', include('recommendations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
