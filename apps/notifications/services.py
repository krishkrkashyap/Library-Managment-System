from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.notifications.models import Notification


class NotificationService:

    @staticmethod
    def send_due_date_reminder(borrow_record):
        member = borrow_record.member
        due_date = borrow_record.due_date.strftime('%B %d, %Y')
        subject = f"Reminder: '{borrow_record.book_instance.book.title}' due on {due_date}"
        message = (
            f"Dear {member.user.get_full_name()},\n\n"
            f"This is a friendly reminder that the book '{borrow_record.book_instance.book.title}' "
            f"you borrowed is due on {due_date}.\n\n"
            f"Please return it to the library by the due date to avoid fines.\n\n"
            f"Thank you,\nLibrary Management System"
        )
        NotificationService.send_notification(
            member=member,
            notification_type='due_date_reminder',
            subject=subject,
            message=message,
        )

    @staticmethod
    def send_overdue_notice(borrow_record):
        member = borrow_record.member
        days_overdue = (timezone.now().date() - borrow_record.due_date).days
        subject = f"Overdue: '{borrow_record.book_instance.book.title}' is {days_overdue} day(s) overdue"
        message = (
            f"Dear {member.user.get_full_name()},\n\n"
            f"The book '{borrow_record.book_instance.book.title}' you borrowed was due on "
            f"{borrow_record.due_date.strftime('%B %d, %Y')} and is now {days_overdue} day(s) overdue.\n\n"
            f"Please return it as soon as possible. Fines are accumulating daily.\n\n"
            f"Thank you,\nLibrary Management System"
        )
        NotificationService.send_notification(
            member=member,
            notification_type='overdue_notice',
            subject=subject,
            message=message,
        )

    @staticmethod
    def send_hold_available(hold):
        member = hold.member
        subject = f"Hold Ready: '{hold.book_instance.book.title}' is available for pickup"
        message = (
            f"Dear {member.user.get_full_name()},\n\n"
            f"Good news! The book '{hold.book_instance.book.title}' you placed on hold "
            f"is now available for pickup.\n\n"
            f"Please collect it from the library within 3 days, or your hold will be cancelled.\n\n"
            f"Thank you,\nLibrary Management System"
        )
        NotificationService.send_notification(
            member=member,
            notification_type='hold_available',
            subject=subject,
            message=message,
        )

    @staticmethod
    def send_notification(member, notification_type, subject, message, sent_via='email'):
        notification = Notification.objects.create(
            member=member,
            notification_type=notification_type,
            subject=subject,
            message=message,
            sent_via=sent_via,
            sent_at=timezone.now(),
        )

        if sent_via == 'email' and member.user.email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member.user.email],
                    fail_silently=False,
                )
            except Exception:
                pass

        return notification
