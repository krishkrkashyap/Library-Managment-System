from django.urls import path
from apps.reports import views

app_name = 'reports'

urlpatterns = [
    path('', views.staff_dashboard, name='staff_dashboard'),
    path('circulation/', views.circulation_report, name='circulation_report'),
    path('popular-books/', views.popular_books_report, name='popular_books_report'),
    path('member-activity/', views.member_activity_report, name='member_activity_report'),
    path('financial/', views.financial_report, name='financial_report'),
    path('export-csv/', views.export_csv, name='export_csv'),
]
