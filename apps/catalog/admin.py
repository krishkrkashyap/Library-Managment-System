from django.contrib import admin
from .models import Publisher, Author, Genre, Language, Book, BookInstance


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at')
    search_fields = ('name',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth')
    search_fields = ('first_name', 'last_name')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'dewey_decimal')
    search_fields = ('name',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'publish_date', 'total_copies', 'available_copies', 'is_active')
    list_filter = ('genres', 'is_active', 'publisher')
    search_fields = ('title', 'authors__first_name', 'authors__last_name', 'isbn_13')
    filter_horizontal = ('authors', 'genres', 'languages')
    inlines = [BookInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'barcode', 'status', 'shelf_location', 'created_at')
    list_filter = ('status',)
    search_fields = ('barcode', 'book__title')
