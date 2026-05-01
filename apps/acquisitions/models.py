from django.db import models


class PurchaseSuggestion(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('ordered', 'Ordered'),
    )

    member = models.ForeignKey(
        'members.MemberProfile',
        on_delete=models.SET_NULL,
        related_name='purchase_suggestions',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=17, blank=True)
    reason = models.TextField(
        help_text="Why should the library acquire this item?",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    reviewed_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        related_name='reviewed_suggestions',
        null=True,
        blank=True,
    )
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
