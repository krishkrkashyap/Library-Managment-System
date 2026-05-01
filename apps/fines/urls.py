from django.urls import path
from . import views

app_name = 'fines'

urlpatterns = [
    path('', views.fine_list, name='fine_list'),
    path('pay/<int:pk>/', views.fine_payment, name='fine_payment'),
    path('waive/<int:pk>/', views.fine_waiver, name='fine_waiver'),
    path('my-fines/', views.my_fines, name='my_fines'),
    path('pay-all/', views.pay_all_fines, name='pay_all'),
    path('pay-fine/<int:pk>/', views.pay_fine, name='pay_fine'),
    path('mark-paid/<int:pk>/', views.mark_paid, name='mark_paid'),
]
