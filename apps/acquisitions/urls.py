from django.urls import path
from apps.acquisitions import views

app_name = 'acquisitions'

urlpatterns = [
    path('suggestions/', views.suggestion_list, name='suggestion_list'),
    path('suggestions/create/', views.suggestion_create, name='suggestion_create'),
    path('suggestions/form/', views.suggestion_create, name='suggestion_form'),
    path('suggestions/<int:pk>/', views.suggestion_detail, name='suggestion_detail'),
    path('suggestions/<int:pk>/approve/', views.approve_suggestion, name='approve_suggestion'),
    path('suggestions/<int:pk>/reject/', views.reject_suggestion, name='reject_suggestion'),
]
