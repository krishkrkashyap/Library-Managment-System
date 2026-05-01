from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('catalog/', include('apps.catalog.urls', namespace='catalog')),
    path('accounts/', include('apps.users.urls', namespace='users')),
    path('members/', include('apps.members.urls', namespace='members')),
    path('circulation/', include('apps.circulation.urls', namespace='circulation')),
    path('fines/', include('apps.fines.urls', namespace='fines')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('acquisitions/', include('apps.acquisitions.urls', namespace='acquisitions')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
