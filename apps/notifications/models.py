from django.db import models
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('due_date_reminder', 'Due Date Reminder'),
        ('overdue_notice', 'Overdue Notice'),
        ('hold_available', 'Hold Available'),
        ('hold_expiring', 'Hold Expiring'),
        ('fine_receipt', 'Fine Receipt'),
        ('membership_expiry', 'Membership Expiry'),
        ('system_announcement', 'System Announcement'),
    )

    SENT_VIA_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    )

    member = models.ForeignKey(
        'members.MemberProfile',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_via = models.CharField(
        max_length=10,
        choices=SENT_VIA_CHOICES,
        default='in_app',
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['member', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        target = self.member.user.get_full_name() if self.member else 'All Users'
        return f"[{self.get_notification_type_display()}] {target} - {self.subject}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
