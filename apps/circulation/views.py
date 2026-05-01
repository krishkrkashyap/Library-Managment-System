from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, F
from django.http import JsonResponse

from apps.catalog.models import BookInstance
from apps.members.models import MemberProfile
from apps.circulation.models import BorrowRecord, HoldReservation
from apps.circulation.services import CirculationService
from apps.circulation.forms import IssueBookForm, ReturnBookForm, HoldForm


def is_librarian(user):
    return user.is_authenticated and user.is_librarian


@login_required
@user_passes_test(is_librarian)
def issue_book(request):
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            book_instance = form.cleaned_data['book_instance']
            member = form.cleaned_data['member']
            try:
                CirculationService.issue_book(
                    book_instance=book_instance,
                    member=member,
                    issued_by=request.user,
                )
                messages.success(request, f'Book "{book_instance.book.title}" issued to {member.user.get_full_name()}.')
                return redirect('circulation:active_loans')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = IssueBookForm()
    return render(request, 'circulation/issue_book.html', {'form': form})


@login_required
@user_passes_test(is_librarian)
def return_book(request):
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            borrow_record = form.cleaned_data['borrow_record']
            try:
                CirculationService.return_book(
                    borrow_record=borrow_record,
                    returned_by=request.user,
                )
                messages.success(request, f'Book "{borrow_record.book_instance.book.title}" returned.')
                if borrow_record.is_overdue:
                    messages.warning(request, f'Overdue by {borrow_record.overdue_days} days. Fine: ${borrow_record.fine_amount}')
                return redirect('circulation:active_loans')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = ReturnBookForm()
    return render(request, 'circulation/return_book.html', {'form': form})


@login_required
@user_passes_test(is_librarian)
def renew_book(request, pk):
    borrow_record = get_object_or_404(BorrowRecord, pk=pk, return_date__isnull=True)
    try:
        CirculationService.renew_book(borrow_record)
        messages.success(request, f'Book renewed. New due date: {borrow_record.due_date}')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('circulation:active_loans')


@login_required
@user_passes_test(is_librarian)
def renew_loan(request, pk):
    return renew_book(request, pk)


@login_required
@user_passes_test(is_librarian)
def active_loans(request):
    loans = CirculationService.get_active_loans()
    search = request.GET.get('search')
    if search:
        loans = loans.filter(
            Q(member__user__first_name__icontains=search)
            | Q(member__user__last_name__icontains=search)
            | Q(book_instance__book__title__icontains=search)
            | Q(book_instance__barcode__icontains=search)
        )
    return render(request, 'circulation/active_loans.html', {'loans': loans})


@login_required
@user_passes_test(is_librarian)
def overdue_books(request):
    overdue = CirculationService.get_overdue_books()
    return render(request, 'circulation/overdue_books.html', {'overdue': overdue})


@login_required
def place_hold(request):
    if request.method == 'POST':
        form = HoldForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            member = form.cleaned_data['member']
            queue_position = HoldReservation.objects.filter(book=book, status__in=['pending', 'ready']).count() + 1
            HoldReservation.objects.create(
                book=book, member=member, queue_position=queue_position,
            )
            messages.success(request, f'Hold placed on "{book.title}". Position: {queue_position}')
            return redirect('circulation:my_holds')
    else:
        form = HoldForm()
    return render(request, 'circulation/place_hold.html', {'form': form})


@login_required
def cancel_hold(request, pk):
    hold = get_object_or_404(HoldReservation, pk=pk)
    if hold.status not in ('pending', 'ready'):
        messages.error(request, 'Cannot cancel this hold.')
        return redirect('circulation:my_holds')
    hold.status = 'cancelled'
    hold.save()
    messages.success(request, f'Hold on "{hold.book.title}" cancelled.')
    return redirect('circulation:my_holds')


@login_required
def my_holds(request):
    holds = HoldReservation.objects.filter(member__user=request.user).select_related('book', 'member').order_by('placed_date')
    return render(request, 'circulation/my_holds.html', {
        'active_holds': holds.filter(status__in=['pending', 'ready']),
        'past_holds': holds.filter(status__in=['fulfilled', 'cancelled', 'expired']),
    })


@login_required
@user_passes_test(is_librarian)
def hold_queue(request):
    status = request.GET.get('status')
    holds = HoldReservation.objects.select_related('book', 'member__user').all()
    if status:
        holds = holds.filter(status=status)
    else:
        holds = holds.filter(status__in=['pending', 'ready'])
    return render(request, 'circulation/hold_queue.html', {'holds': holds.order_by('book', 'placed_date')})


@login_required
@user_passes_test(is_librarian)
def lookup_book(request):
    barcode = request.GET.get('barcode', '')
    result = {}
    if barcode:
        try:
            instance = BookInstance.objects.select_related('book').get(barcode=barcode)
            result = {'title': instance.book.title, 'barcode': instance.barcode, 'status': instance.status, 'id': instance.id}
        except BookInstance.DoesNotExist:
            result = {'error': 'Book not found'}
    return JsonResponse(result)


@login_required
@user_passes_test(is_librarian)
def lookup_member(request):
    member_id = request.GET.get('membership_id', '')
    result = {}
    if member_id:
        try:
            member = MemberProfile.objects.select_related('user').get(membership_id=member_id)
            result = {'name': member.user.get_full_name(), 'id': member.membership_id, 'status': member.status, 'can_borrow': member.can_borrow}
        except MemberProfile.DoesNotExist:
            result = {'error': 'Member not found'}
    return JsonResponse(result)


@login_required
@user_passes_test(is_librarian)
def lookup_return(request):
    barcode = request.GET.get('barcode', '')
    result = {}
    if barcode:
        try:
            instance = BookInstance.objects.get(barcode=barcode)
            record = BorrowRecord.objects.select_related('book_instance__book', 'member__user').get(book_instance=instance, return_date__isnull=True)
            result = {
                'title': record.book_instance.book.title,
                'member': record.member.user.get_full_name(),
                'due_date': record.due_date.strftime('%Y-%m-%d'),
                'is_overdue': record.is_overdue,
                'overdue_days': record.overdue_days,
            }
        except (BookInstance.DoesNotExist, BorrowRecord.DoesNotExist):
            result = {'error': 'No active loan found'}
    return JsonResponse(result)
