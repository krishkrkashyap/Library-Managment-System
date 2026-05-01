from django.utils import timezone
from decimal import Decimal

from apps.fines.models import Fine
from apps.circulation.models import BorrowRecord


class FineCalculator:
    """Calculates fines for overdue, lost, and damaged books."""

    @staticmethod
    def calculate_overdue_fine(borrow_record):
        if not borrow_record.is_overdue:
            return None

        existing_fine = Fine.objects.filter(
            borrow_record=borrow_record,
            fine_type='overdue',
            is_paid=False,
        ).first()

        if existing_fine:
            return existing_fine

        overdue_days = borrow_record.overdue_days
        daily_rate = borrow_record.member.category.daily_fine_rate
        max_fine = borrow_record.member.category.max_fine_amount

        calculated_amount = Decimal(overdue_days) * daily_rate
        fine_amount = min(calculated_amount, max_fine)

        fine = Fine.objects.create(
            member=borrow_record.member,
            borrow_record=borrow_record,
            fine_type='overdue',
            amount=fine_amount,
            issued_date=timezone.now().date(),
            notes=f'Overdue by {overdue_days} days at {daily_rate}/day (max: {max_fine})',
        )

        return fine

    @staticmethod
    def calculate_all_overdue_fines():
        overdue_records = BorrowRecord.objects.filter(
            return_date__isnull=True,
            due_date__lt=timezone.now().date(),
        )

        created_fines = []
        for record in overdue_records:
            existing = Fine.objects.filter(
                borrow_record=record,
                fine_type='overdue',
                is_paid=False,
            ).exists()
            if not existing:
                fine = FineCalculator.calculate_overdue_fine(record)
                if fine:
                    created_fines.append(fine)

        return created_fines

    @staticmethod
    def calculate_lost_fine(borrow_record, amount=None):
        if amount is None:
            book = borrow_record.book_instance.book
            amount = borrow_record.book_instance.acquisition_cost or Decimal('50.00')

        fine = Fine.objects.create(
            member=borrow_record.member,
            borrow_record=borrow_record,
            fine_type='lost',
            amount=amount,
            issued_date=timezone.now().date(),
            notes=f'Lost book: {borrow_record.book_instance}',
        )

        return fine

    @staticmethod
    def calculate_damaged_fine(borrow_record, amount, notes=''):
        fine = Fine.objects.create(
            member=borrow_record.member,
            borrow_record=borrow_record,
            fine_type='damaged',
            amount=amount,
            issued_date=timezone.now().date(),
            notes=notes or f'Damaged book: {borrow_record.book_instance}',
        )

        return fine
