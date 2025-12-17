from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),

    # Redoc
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc'
    ),
    path("auth/", include("accounts.urls")),
    path('posts/',include('posts.urls')),
    path('onboarding/',include('onboarding.urls')),
    path('profiles/',include('profiles.urls')),
    path('activity/',include('activity.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)