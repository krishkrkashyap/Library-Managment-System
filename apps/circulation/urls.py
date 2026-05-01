from django.urls import path
from . import views

app_name = 'circulation'

urlpatterns = [
    path('issue/', views.issue_book, name='issue_book'),
    path('return/', views.return_book, name='return_book'),
    path('renew/<int:pk>/', views.renew_loan, name='renew_loan'),
    path('active-loans/', views.active_loans, name='active_loans'),
    path('overdue/', views.overdue_books, name='overdue_books'),
    path('hold/place/', views.place_hold, name='place_hold'),
    path('hold/<int:pk>/cancel/', views.cancel_hold, name='cancel_hold'),
    path('my-holds/', views.my_holds, name='my_holds'),
    path('hold-queue/', views.hold_queue, name='hold_queue'),
    path('lookup-book/', views.lookup_book, name='lookup_book'),
    path('lookup-member/', views.lookup_member, name='lookup_member'),
    path('lookup-return/', views.lookup_return, name='lookup_return'),
]
