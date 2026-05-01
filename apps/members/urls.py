from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('create/', views.member_create, name='member_create'),
    path('<int:pk>/edit/', views.member_update, name='member_update'),
    path('dashboard/', views.patron_dashboard, name='patron_dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
]
