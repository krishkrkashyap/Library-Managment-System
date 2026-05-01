from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from .models import Book, Author, Genre, Publisher, BookInstance
from .filters import BookFilter
from .forms import BookForm, AuthorForm, PublisherForm, BookInstanceForm


def is_librarian(user):
    return user.is_authenticated and user.is_librarian


def book_list(request):
    books = Book.objects.filter(is_active=True).select_related('publisher').prefetch_related('authors', 'genres')
    book_filter = BookFilter(request.GET, queryset=books)
    
    context = {
        'filter': book_filter,
        'books': book_filter.qs,
        'genres': Genre.objects.all(),
        'search_query': request.GET.get('search', ''),
    }
    return render(request, 'catalog/book_list.html', context)


def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    instances = book.instances.all()
    related_books = Book.objects.filter(genres__in=book.genres.all()).exclude(id=book.id).distinct()[:6]
    
    context = {
        'book': book,
        'instances': instances,
        'related_books': related_books,
    }
    return render(request, 'catalog/book_detail.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_librarian), name='dispatch')
class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'catalog/book_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Book added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('catalog:book_detail', kwargs={'slug': self.object.slug})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_librarian), name='dispatch')
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'catalog/book_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Book updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_librarian), name='dispatch')
class BookDeleteView(DeleteView):
    model = Book
    template_name = 'catalog/book_confirm_delete.html'
    success_url = reverse_lazy('catalog:book_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Book removed successfully!')
        return super().delete(request, *args, **kwargs)


def author_list(request):
    authors = Author.objects.annotate(book_count=Count('books')).order_by('last_name', 'first_name')
    return render(request, 'catalog/author_list.html', {'authors': authors})


def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    books = author.books.filter(is_active=True)
    return render(request, 'catalog/author_detail.html', {'author': author, 'books': books})


def genre_list(request):
    genres = Genre.objects.filter(parent__isnull=True).annotate(book_count=Count('books'))
    return render(request, 'catalog/genre_list.html', {'genres': genres})


def genre_detail(request, pk):
    genre = get_object_or_404(Genre, pk=pk)
    books = genre.books.filter(is_active=True)
    children = genre.children.all()
    return render(request, 'catalog/genre_detail.html', {
        'genre': genre,
        'books': books,
        'children': children,
    })


@login_required
@user_passes_test(is_librarian)
def isbn_import(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn', '').strip()
        if isbn:
            from services.search_service import SearchService
            book_data = SearchService.fetch_book_by_isbn(isbn)
            if book_data:
                messages.success(request, 'Book data fetched from Google Books. Please review and save.')
                return render(request, 'catalog/isbn_import.html', {'book_data': book_data, 'isbn': isbn})
            else:
                messages.error(request, 'No book found with that ISBN.')
        else:
            messages.error(request, 'Please enter a valid ISBN.')
    return render(request, 'catalog/isbn_import.html')


@login_required
@user_passes_test(is_librarian)
def import_book_from_isbn(request):
    if request.method == 'POST':
        from services.search_service import SearchService
        book = SearchService.create_book_from_isbn_data(request.POST)
        if book:
            messages.success(request, f'Book "{book.title}" imported successfully!')
            return redirect('catalog:book_detail', slug=book.slug)
        else:
            messages.error(request, 'Failed to import book. Please check the data.')
    return redirect('catalog:isbn_import')
