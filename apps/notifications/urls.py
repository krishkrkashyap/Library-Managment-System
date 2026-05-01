from django.urls import path
from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:notification_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
