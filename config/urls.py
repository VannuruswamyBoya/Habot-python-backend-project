from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/swagger/', permanent=False), name='index'),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    
    # OpenAPI and Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # App URLs
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/lsas/', include('apps.lsas.urls')),
    path('api/v1/parents/', include('apps.parents.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    
    # Auth URLs
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
