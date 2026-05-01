from django.contrib import admin
from .models import Fine


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'fine_type',
        'amount',
        'issued_date',
        'is_paid',
        'paid_date',
        'payment_method',
    )
    list_filter = ('fine_type', 'is_paid', 'payment_method', 'issued_date')
    search_fields = (
        'member__user__first_name',
        'member__user__last_name',
        'member__membership_id',
        'notes',
    )
    date_hierarchy = 'issued_date'
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_paid', 'waive_selected']

    @admin.action(description='Mark selected fines as paid')
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(is_paid=False).update(is_paid=True)
        self.message_user(request, f'{updated} fine(s) marked as paid.')

    @admin.action(description='Waive selected fines')
    def waive_selected(self, request, queryset):
        updated = queryset.filter(is_paid=False).update(
            is_paid=True,
            payment_method='waived',
            waiver_reason='Waived via admin action',
        )
        self.message_user(request, f'{updated} fine(s) waived.')
