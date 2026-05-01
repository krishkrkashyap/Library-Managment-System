import django_filters
from .models import Book, Author, Genre


class BookFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    genre = django_filters.ModelMultipleChoiceFilter(field_name='genres', queryset=Genre.objects.all())
    author = django_filters.ModelChoiceFilter(field_name='authors', queryset=Author.objects.all())
    available = django_filters.BooleanFilter(method='filter_available')
    
    class Meta:
        model = Book
        fields = ['search', 'genre', 'author', 'available']
    
    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(authors__first_name__icontains=value) |
                Q(authors__last_name__icontains=value) |
                Q(isbn_13__icontains=value) |
                Q(subject_keywords__icontains=value)
            ).distinct()
        return queryset
    
    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(available_copies__gt=0)
        return queryset
