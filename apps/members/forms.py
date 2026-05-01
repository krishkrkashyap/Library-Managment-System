from django import forms
from .models import MemberProfile, PatronCategory


class PatronCategoryForm(forms.ModelForm):
    class Meta:
        model = PatronCategory
        fields = ['name', 'description', 'max_books_allowed', 'loan_period_days', 'max_renewals', 
                  'renewal_period_days', 'daily_fine_rate', 'max_fine_amount', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'max_books_allowed': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'loan_period_days': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'max_renewals': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'renewal_period_days': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'daily_fine_rate': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'max_fine_amount': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ['category', 'phone_number', 'address', 'date_of_birth', 'photo',
                  'membership_start', 'membership_expiry', 'status', 'emergency_contact_name',
                  'emergency_contact_phone', 'notes', 'is_blocked']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'membership_start': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'membership_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }


class MemberRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}), label='Confirm Password')
    
    class Meta:
        model = MemberProfile
        fields = ['category', 'phone_number', 'address', 'date_of_birth', 'membership_start']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'membership_start': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data
