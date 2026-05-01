from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class PatronCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_books_allowed = models.PositiveIntegerField(default=5)
    loan_period_days = models.PositiveIntegerField(default=14)
    max_renewals = models.PositiveIntegerField(default=2)
    renewal_period_days = models.PositiveIntegerField(default=14)
    daily_fine_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.50)
    max_fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=25.00)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class MemberProfile(models.Model):
    MEMBERSHIP_STATUS = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending Approval'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member_profile')
    membership_id = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(PatronCategory, on_delete=models.PROTECT, related_name='members')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='member_photos/', blank=True)
    membership_start = models.DateField()
    membership_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True, help_text="Staff-only notes")
    is_blocked = models.BooleanField(default=False, help_text="Blocks new checkouts if fines exceed limit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.membership_id})"
    
    def save(self, *args, **kwargs):
        if not self.membership_id:
            self.membership_id = self.generate_membership_id()
        if not self.membership_expiry:
            self.membership_expiry = self.membership_start + timedelta(days=365)
        super().save(*args, **kwargs)
    
    def generate_membership_id(self):
        year = timezone.now().year
        last_member = MemberProfile.objects.filter(membership_id__startswith=f'MEM-{year}-').order_by('-pk').first()
        if last_member:
            last_num = int(last_member.membership_id.split('-')[-1])
            return f"MEM-{year}-{last_num + 1:04d}"
        return f"MEM-{year}-0001"
    
    @property
    def total_fines(self):
        from apps.fines.models import Fine
        unpaid = Fine.objects.filter(member=self, is_paid=False).aggregate(total=models.Sum('amount'))
        return unpaid['total'] or 0
    
    @property
    def can_borrow(self):
        current_borrows = self.borrow_records.filter(return_date__isnull=True).count()
        return (
            self.status == 'active'
            and not self.is_blocked
            and current_borrows < self.category.max_books_allowed
            and self.total_fines < self.category.max_fine_amount
        )
    
    @property
    def active_loans_count(self):
        return self.borrow_records.filter(return_date__isnull=True).count()
    
    @property
    def overdue_loans_count(self):
        count = 0
        for record in self.borrow_records.filter(return_date__isnull=True):
            if record.is_overdue:
                count += 1
        return count
