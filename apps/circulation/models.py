from django.db import models
from django.utils import timezone
from datetime import timedelta

from apps.catalog.models import Book, BookInstance
from apps.members.models import MemberProfile
from apps.users.models import CustomUser


class BorrowRecord(models.Model):
    book_instance = models.ForeignKey(
        BookInstance,
        on_delete=models.PROTECT,
        related_name='borrow_records',
    )
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.PROTECT,
        related_name='borrow_records',
    )
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    renewed_count = models.PositiveIntegerField(default=0)
    issued_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='issued_records',
    )
    returned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='returned_records',
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['member', 'return_date']),
            models.Index(fields=['book_instance', 'return_date']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.book_instance} -> {self.member} ({self.issue_date})"

    @property
    def is_overdue(self):
        if self.return_date:
            return self.return_date > self.due_date
        return timezone.now().date() > self.due_date

    @property
    def overdue_days(self):
        if self.return_date:
            if self.return_date > self.due_date:
                return (self.return_date - self.due_date).days
            return 0
        days = (timezone.now().date() - self.due_date).days
        return max(days, 0)

    @property
    def fine_amount(self):
        if not self.is_overdue:
            return 0
        from apps.fines.models import Fine
        fines = Fine.objects.filter(
            borrow_record=self,
            is_paid=False,
        )
        return sum(f.amount for f in fines)


class HoldReservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('ready', 'Ready for Pickup'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='hold_reservations',
    )
    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='hold_reservations',
    )
    placed_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    fulfilled_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    notification_sent = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)
    freeze_until = models.DateField(null=True, blank=True)
    pickup_branch = models.CharField(max_length=255, blank=True)
    queue_position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['placed_date']
        indexes = [
            models.Index(fields=['book', 'status']),
            models.Index(fields=['member', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Hold: {self.book} for {self.member} ({self.status})"

    @property
    def is_active(self):
        return self.status in ('pending', 'ready')

    @property
    def is_expired(self):
        if self.status in ('fulfilled', 'cancelled', 'expired'):
            return True
        return timezone.now().date() > self.expiry_date

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = self.placed_date + timedelta(days=30)
        super().save(*args, **kwargs)
