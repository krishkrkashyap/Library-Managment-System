from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('book/add/', views.BookCreateView.as_view(), name='book_add'),
    path('book/<slug:slug>/edit/', views.BookUpdateView.as_view(), name='book_edit'),
    path('book/<slug:slug>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    
    path('genres/', views.genre_list, name='genre_list'),
    path('genres/<int:pk>/', views.genre_detail, name='genre_detail'),
    
    path('isbn-import/', views.isbn_import, name='isbn_import'),
    path('isbn-import/create/', views.import_book_from_isbn, name='isbn_import_create'),
]
