from django import forms
from apps.acquisitions.models import PurchaseSuggestion


class PurchaseSuggestionForm(forms.ModelForm):
    class Meta:
        model = PurchaseSuggestion
        fields = ('title', 'author', 'isbn', 'reason')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter book title',
            }),
            'author': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter author name',
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter ISBN-10 or ISBN-13',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Explain why the library should acquire this item...',
            }),
        }
        labels = {
            'title': 'Book Title',
            'author': 'Author',
            'isbn': 'ISBN',
            'reason': 'Reason for Suggestion',
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').strip()
        if isbn:
            cleaned = isbn.replace('-', '').replace(' ', '')
            if len(cleaned) not in (10, 13) or not cleaned.isdigit():
                raise forms.ValidationError('ISBN must be 10 or 13 digits.')
        return isbn
