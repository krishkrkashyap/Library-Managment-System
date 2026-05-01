from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import timedelta

from apps.catalog.models import BookInstance
from apps.circulation.models import BorrowRecord, HoldReservation
from apps.fines.services import FineCalculator


class CirculationService:
    """Handles all circulation operations: issuing, returning, and renewing books."""

    @staticmethod
    @transaction.atomic
    def issue_book(book_instance, member, issued_by, due_date=None, notes=''):
        if book_instance.status != 'available':
            raise ValidationError(f'Book instance "{book_instance.barcode}" is not available (status: {book_instance.status}).')

        if not member.can_borrow:
            raise ValidationError('Member is not eligible to borrow books. Check membership status, blocks, or outstanding fines.')

        if due_date is None:
            due_date = timezone.now().date() + timedelta(days=member.category.loan_period_days)

        borrow_record = BorrowRecord.objects.create(
            book_instance=book_instance,
            member=member,
            issue_date=timezone.now().date(),
            due_date=due_date,
            issued_by=issued_by,
            notes=notes,
        )

        book_instance.status = 'on_loan'
        book_instance.save()

        book = book_instance.book
        book.available_copies = max(0, book.available_copies - 1)
        book.save()

        return borrow_record

    @staticmethod
    @transaction.atomic
    def return_book(borrow_record, returned_by, condition_notes=''):
        if borrow_record.return_date is not None:
            raise ValidationError('This book has already been returned.')

        borrow_record.return_date = timezone.now().date()
        borrow_record.returned_by = returned_by
        if condition_notes:
            borrow_record.notes = f"{borrow_record.notes}\nReturn notes: {condition_notes}".strip()
        borrow_record.save()

        book_instance = borrow_record.book_instance
        book_instance.status = 'available'
        book_instance.save()

        book = book_instance.book
        book.available_copies += 1
        book.save()

        if borrow_record.is_overdue:
            FineCalculator.calculate_overdue_fine(borrow_record)

        return borrow_record

    @staticmethod
    @transaction.atomic
    def renew_book(borrow_record):
        if borrow_record.return_date is not None:
            raise ValidationError('This book has already been returned and cannot be renewed.')

        member = borrow_record.member
        if borrow_record.renewed_count >= member.category.max_renewals:
            raise ValidationError('Maximum number of renewals reached for this loan.')

        if borrow_record.is_overdue:
            raise ValidationError('Cannot renew an overdue book. Please return and re-borrow.')

        book_instance = borrow_record.book_instance
        pending_holds = HoldReservation.objects.filter(
            book=book_instance.book,
            status='pending',
        )
        if pending_holds.exists():
            raise ValidationError('Cannot renew: this book has pending hold reservations.')

        renewal_days = member.category.renewal_period_days
        current_due = borrow_record.due_date
        new_due = current_due + timedelta(days=renewal_days)

        borrow_record.due_date = new_due
        borrow_record.renewed_count += 1
        borrow_record.save()

        return borrow_record

    @staticmethod
    def get_active_loans(member=None):
        queryset = BorrowRecord.objects.select_related(
            'book_instance',
            'book_instance__book',
            'member',
            'member__user',
            'issued_by',
        ).filter(return_date__isnull=True)
        if member:
            queryset = queryset.filter(member=member)
        return queryset.order_by('due_date')

    @staticmethod
    def get_overdue_books():
        today = timezone.now().date()
        return BorrowRecord.objects.select_related(
            'book_instance',
            'book_instance__book',
            'member',
            'member__user',
            'issued_by',
        ).filter(
            return_date__isnull=True,
            due_date__lt=today,
        ).order_by('due_date')
