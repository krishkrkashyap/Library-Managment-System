from django.contrib import admin
from apps.acquisitions.models import PurchaseSuggestion


@admin.register(PurchaseSuggestion)
class PurchaseSuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'member', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
