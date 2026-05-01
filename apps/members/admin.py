from django.contrib import admin
from .models import MemberProfile, PatronCategory


@admin.register(PatronCategory)
class PatronCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_books_allowed', 'loan_period_days', 'daily_fine_rate', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_id', 'category', 'status', 'membership_start', 'membership_expiry', 'is_blocked')
    list_filter = ('status', 'category', 'is_blocked')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'membership_id')
    date_hierarchy = 'membership_start'
