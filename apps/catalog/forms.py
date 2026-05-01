from django import forms
from .models import Book, Author, Publisher, BookInstance


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn_10', 'isbn_13', 'authors', 'publisher',
            'publish_date', 'edition', 'pages', 'genres', 'languages',
            'description', 'cover_image', 'dewey_decimal', 'lc_classification',
            'subject_keywords', 'total_copies', 'available_copies', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'subtitle': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'isbn_10': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'isbn_13': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'publish_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'edition': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'pages': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'dewey_decimal': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'lc_classification': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'subject_keywords': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Fiction, Mystery, Thriller'}),
            'total_copies': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'available_copies': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'biography', 'date_of_birth', 'date_of_death', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'biography': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'barcode', 'call_number', 'status', 'acquisition_date', 'acquisition_cost', 'shelf_location', 'notes']
        widgets = {
            'barcode': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'call_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'acquisition_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'acquisition_cost': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'shelf_location': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }
