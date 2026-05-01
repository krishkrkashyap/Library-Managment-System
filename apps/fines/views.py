from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum
from django.views.decorators.http import require_POST

from apps.fines.models import Fine


def is_librarian(user):
    return user.is_authenticated and user.is_librarian


@login_required
@user_passes_test(is_librarian)
def fine_list(request):
    fines = Fine.objects.select_related(
        'member',
        'member__user',
        'borrow_record',
        'borrow_record__book_instance',
        'borrow_record__book_instance__book',
    ).all()

    status = request.GET.get('status')
    if status == 'unpaid':
        fines = fines.filter(is_paid=False)
    elif status == 'paid':
        fines = fines.filter(is_paid=True)

    fine_type = request.GET.get('type')
    if fine_type:
        fines = fines.filter(fine_type=fine_type)

    search = request.GET.get('search')
    if search:
        fines = fines.filter(
            Q(member__user__first_name__icontains=search)
            | Q(member__user__last_name__icontains=search)
            | Q(member__membership_id__icontains=search)
        )

    total_unpaid = Fine.objects.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
    total_paid = Fine.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'fines/fine_list.html', {
        'fines': fines,
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
        'current_status': status,
        'current_type': fine_type,
        'search_query': search or '',
    })


@login_required
def fine_payment(request, pk):
    fine = get_object_or_404(Fine, pk=pk)

    if fine.is_paid:
        messages.info(request, 'This fine has already been paid.')
        return redirect('fines:my_fines')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cash')
        if payment_method not in dict(Fine.PAYMENT_METHOD_CHOICES):
            messages.error(request, 'Invalid payment method.')
        else:
            try:
                fine.pay(payment_method=payment_method)
                messages.success(request, f'Fine of ${fine.amount} has been paid via {fine.get_payment_method_display()}.')
            except ValueError as e:
                messages.error(request, str(e))

        return redirect('fines:my_fines')

    return render(request, 'fines/fine_payment.html', {'fine': fine})


@login_required
@user_passes_test(is_librarian)
def fine_waiver(request, pk):
    fine = get_object_or_404(Fine, pk=pk)

    if fine.is_paid:
        messages.info(request, 'This fine has already been paid or waived.')
        return redirect('fines:fine_list')

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        if not reason:
            messages.error(request, 'A waiver reason is required.')
        else:
            try:
                fine.waive(user=request.user, reason=reason)
                messages.success(request, f'Fine of ${fine.amount} has been waived.')
            except ValueError as e:
                messages.error(request, str(e))

        return redirect('fines:fine_list')

    return render(request, 'fines/fine_waiver.html', {'fine': fine})


@login_required
def my_fines(request):
    fines = Fine.objects.filter(
        member__user=request.user,
    ).select_related('borrow_record', 'borrow_record__book_instance', 'borrow_record__book_instance__book')

    unpaid_fines = fines.filter(is_paid=False)
    paid_fines = fines.filter(is_paid=True)

    total_unpaid = unpaid_fines.aggregate(total=Sum('amount'))['total'] or 0
    total_paid = paid_fines.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'fines/my_fines.html', {
        'fines': unpaid_fines,
        'total': total_unpaid,
    })


@login_required
@require_POST
def pay_all_fines(request):
    fines = Fine.objects.filter(member__user=request.user, is_paid=False)
    for fine in fines:
        fine.pay(payment_method='cash')
    messages.success(request, 'All fines paid successfully.')
    return redirect('fines:my_fines')


@login_required
@require_POST
def pay_fine(request, pk):
    fine = get_object_or_404(Fine, pk=pk, member__user=request.user)
    if not fine.is_paid:
        fine.pay(payment_method='cash')
        messages.success(request, f'Fine of ${fine.amount} paid.')
    return redirect('fines:my_fines')


@login_required
@user_passes_test(is_librarian)
@require_POST
def mark_paid(request, pk):
    fine = get_object_or_404(Fine, pk=pk)
    if not fine.is_paid:
        fine.pay(payment_method='cash')
        messages.success(request, f'Fine of ${fine.amount} marked as paid.')
    return redirect('fines:fine_list')
