from django import forms
from django.utils import timezone
from datetime import timedelta

from apps.catalog.models import BookInstance
from apps.members.models import MemberProfile
from apps.circulation.models import BorrowRecord, HoldReservation


class IssueBookForm(forms.Form):
    book_instance = forms.ModelChoiceField(
        queryset=BookInstance.objects.filter(status='available'),
        label='Book Instance',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )
    member = forms.ModelChoiceField(
        queryset=MemberProfile.objects.filter(status='active'),
        label='Member',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )
    due_date = forms.DateField(
        label='Due Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        required=False,
    )
    notes = forms.CharField(
        label='Notes',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('due_date'):
            self.initial['due_date'] = timezone.now().date() + timedelta(days=14)

    def clean_book_instance(self):
        book_instance = self.cleaned_data.get('book_instance')
        if book_instance and book_instance.status != 'available':
            raise forms.ValidationError('This book instance is not available for checkout.')
        return book_instance

    def clean_member(self):
        member = self.cleaned_data.get('member')
        if member and not member.can_borrow:
            raise forms.ValidationError('This member cannot borrow books. Check membership status, blocks, or outstanding fines.')
        return member


class ReturnBookForm(forms.Form):
    borrow_record = forms.ModelChoiceField(
        queryset=BorrowRecord.objects.filter(return_date__isnull=True),
        label='Loan Record',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )
    condition_notes = forms.CharField(
        label='Condition Notes',
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        help_text='Optional: Note any damage or issues with the returned book.',
    )

    def clean_borrow_record(self):
        borrow_record = self.cleaned_data.get('borrow_record')
        if borrow_record and borrow_record.return_date is not None:
            raise forms.ValidationError('This book has already been returned.')
        return borrow_record


class HoldForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=None,
        label='Book',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )
    member = forms.ModelChoiceField(
        queryset=MemberProfile.objects.filter(status='active'),
        label='Member',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )
    expiry_date = forms.DateField(
        label='Expiry Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        required=False,
    )
    pickup_branch = forms.CharField(
        label='Pickup Branch',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.catalog.models import Book
        self.fields['book'].queryset = Book.objects.filter(is_active=True)
        if not self.initial.get('expiry_date'):
            self.initial['expiry_date'] = timezone.now().date() + timedelta(days=30)

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        member = cleaned_data.get('member')
        if book and member:
            existing = HoldReservation.objects.filter(
                book=book,
                member=member,
                status__in=['pending', 'ready'],
            )
            if existing.exists():
                raise forms.ValidationError('This member already has an active hold on this book.')
        return cleaned_data
