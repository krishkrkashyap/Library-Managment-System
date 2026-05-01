from django.db import models
from django.utils import timezone

from apps.members.models import MemberProfile
from apps.circulation.models import BorrowRecord


class Fine(models.Model):
    FINE_TYPE_CHOICES = (
        ('overdue', 'Overdue'),
        ('lost', 'Lost Book'),
        ('damaged', 'Damaged Book'),
        ('membership', 'Membership Fee'),
        ('other', 'Other'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('online', 'Online Payment'),
        ('waived', 'Waived'),
    )

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='fines',
    )
    borrow_record = models.ForeignKey(
        BorrowRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fines',
    )
    fine_type = models.CharField(
        max_length=20,
        choices=FINE_TYPE_CHOICES,
        default='overdue',
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    issued_date = models.DateField(default=timezone.now)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
    )
    waived_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waived_fines',
    )
    waiver_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['member', 'is_paid']),
            models.Index(fields=['fine_type']),
            models.Index(fields=['is_paid', 'issued_date']),
        ]

    def __str__(self):
        return f"{self.get_fine_type_display()} - {self.member} (${self.amount})"

    def pay(self, payment_method='cash'):
        if self.is_paid:
            raise ValueError('Fine is already paid')
        self.is_paid = True
        self.paid_date = timezone.now().date()
        self.payment_method = payment_method
        self.save()

    def waive(self, user, reason=''):
        if self.is_paid:
            raise ValueError('Fine is already paid')
        self.is_paid = True
        self.paid_date = timezone.now().date()
        self.payment_method = 'waived'
        self.waived_by = user
        self.waiver_reason = reason
        self.save()
