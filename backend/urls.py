from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView
import os

# Frontend view
def frontend_view(request, page='index'):
    try:
        frontend_path = os.path.join(settings.BASE_DIR, 'FRONTEND', f'{page}.html')
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('<h1>Page not found</h1>', status=404)
    except Exception as e:
        return HttpResponse(f'<h1>Error: {str(e)}</h1>', status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Frontend routes
    path('', lambda r: frontend_view(r, 'index')),
    path('index.html', lambda r: frontend_view(r, 'index')),
    path('login/', lambda r: frontend_view(r, 'login')),
    path('login.html', lambda r: frontend_view(r, 'login')),
    path('register/', lambda r: frontend_view(r, 'register')),
    path('register.html', lambda r: frontend_view(r, 'register')),
    path('student-dashboard/', lambda r: frontend_view(r, 'student-dash')),
    path('student-dashboard.html', lambda r: frontend_view(r, 'student-dash')),
    path('student-dash.html', lambda r: frontend_view(r, 'student-dash')),
    path('owner-dashboard/', lambda r: frontend_view(r, 'owner-dash')),
    path('owner-dashboard.html', lambda r: frontend_view(r, 'owner-dash')),
    path('owner-dash.html', lambda r: frontend_view(r, 'owner-dash')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
