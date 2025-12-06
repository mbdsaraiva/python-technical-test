from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin do Django
    path('admin/', admin.site.urls),
    
    # Páginas HTML e APIs (tudo no core)
    path('', include('core.urls')),
    
    # Interface navegável do DRF (para testes)
    path('api-auth/', include('rest_framework.urls')),
]