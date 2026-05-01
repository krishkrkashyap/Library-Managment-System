import csv
from datetime import datetime, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from django.db.models.functions import TruncDate

from apps.catalog.models import Book, BookInstance
from apps.members.models import MemberProfile
from apps.circulation.models import BorrowRecord, HoldReservation
from apps.fines.models import Fine
from apps.users.models import CustomUser


def is_staff(user):
    return user.is_authenticated and user.is_staff_role


@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    total_books = Book.objects.filter(is_active=True).count()
    active_loans = BorrowRecord.objects.filter(return_date__isnull=True).count()
    overdue_books = BorrowRecord.objects.filter(
        return_date__isnull=True,
        due_date__lt=now.date(),
    ).count()
    total_members = MemberProfile.objects.filter(status='active').count()
    total_fines = Fine.objects.aggregate(total=Sum('amount'))['total'] or 0
    unpaid_fines = Fine.objects.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0

    recent_activity = BorrowRecord.objects.select_related(
        'member__user',
        'book_instance__book',
    ).order_by('-issue_date')[:10]

    holds = HoldReservation.objects.filter(
        status__in=['pending', 'ready'],
    ).select_related('member__user', 'book').order_by('-placed_date')[:5]

    context = {
        'total_books': total_books,
        'active_loans': active_loans,
        'overdue_books': overdue_books,
        'total_members': total_members,
        'total_fines': total_fines,
        'unpaid_fines': unpaid_fines,
        'recent_activity': recent_activity,
        'recent_holds': holds,
    }
    return render(request, 'reports/staff_dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def circulation_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end = timezone.now().date()
        start = end - timedelta(days=30)

    loans = BorrowRecord.objects.filter(issue_date__range=[start, end])
    total_checkouts = loans.count()
    total_returns = loans.filter(return_date__isnull=False).count()
    total_renewals = loans.aggregate(total=Sum('renewed_count'))['total'] or 0

    daily_checkouts = (
        loans.annotate(date=TruncDate('issue_date'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    overdue_count = BorrowRecord.objects.filter(
        return_date__isnull=True,
        due_date__lt=end,
    ).count()

    context = {
        'start_date': start,
        'end_date': end,
        'total_checkouts': total_checkouts,
        'total_returns': total_returns,
        'total_renewals': total_renewals,
        'overdue_count': overdue_count,
        'daily_checkouts': daily_checkouts,
    }
    return render(request, 'reports/circulation_report.html', context)


@login_required
@user_passes_test(is_staff)
def popular_books_report(request):
    top_books = (
        Book.objects.filter(is_active=True)
        .annotate(borrow_count=Count('instances__borrowrecord'))
        .order_by('-borrow_count')[:20]
    )

    context = {
        'top_books': top_books,
    }
    return render(request, 'reports/popular_books.html', context)


@login_required
@user_passes_test(is_staff)
def member_activity_report(request):
    active_members = (
        MemberProfile.objects.filter(status='active')
        .annotate(
            total_loans=Count('borrow_records'),
            active_loans=Count('borrow_records', filter=Q(borrow_records__return_date__isnull=True)),
            total_fines=Sum('borrow_records__fine__amount', filter=Q(borrow_records__fine__isnull=False)),
        )
        .select_related('user', 'category')
        .order_by('-total_loans')[:50]
    )

    context = {
        'active_members': active_members,
    }
    return render(request, 'reports/member_activity.html', context)


@login_required
@user_passes_test(is_staff)
def financial_report(request):
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    total_revenue = Fine.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    pending_revenue = Fine.objects.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
    month_revenue = Fine.objects.filter(
        is_paid=True,
        paid_date__gte=this_month_start,
    ).aggregate(total=Sum('amount'))['total'] or 0
    last_month_revenue = Fine.objects.filter(
        is_paid=True,
        paid_date__gte=last_month_start,
        paid_date__lt=this_month_start,
    ).aggregate(total=Sum('amount'))['total'] or 0

    fine_breakdown = (
        Fine.objects.filter(is_paid=True)
        .values('fine_type')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    context = {
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'month_revenue': month_revenue,
        'last_month_revenue': last_month_revenue,
        'fine_breakdown': fine_breakdown,
    }
    return render(request, 'reports/financial_report.html', context)


@login_required
@user_passes_test(is_staff)
def export_csv(request):
    model = request.GET.get('model')
    fields_param = request.GET.get('fields', '')
    fields = [f.strip() for f in fields_param.split(',') if f.strip()]

    model_map = {
        'books': Book,
        'members': MemberProfile,
        'borrow_records': BorrowRecord,
        'fines': Fine,
    }

    if model not in model_map:
        return HttpResponse('Invalid model.', status=400)

    qs = model_map[model].objects.all()
    filename = f'{model}_export_{timezone.now().strftime("%Y%m%d")}.csv'

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(fields)

    for obj in qs:
        row = []
        for field in fields:
            value = getattr(obj, field, None)
            if value is None:
                row.append('')
            elif hasattr(value, 'strftime'):
                row.append(value.strftime('%Y-%m-%d'))
            else:
                row.append(str(value))
        writer.writerow(row)

    return response
