from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.acquisitions.models import PurchaseSuggestion
from apps.acquisitions.forms import PurchaseSuggestionForm
from apps.users.models import CustomUser


def is_staff(user):
    return user.is_authenticated and user.is_staff_role


@login_required
@user_passes_test(is_staff)
def suggestion_list(request):
    status_filter = request.GET.get('status', 'all')

    suggestions = PurchaseSuggestion.objects.select_related(
        'member__user',
        'reviewed_by',
    ).order_by('-created_at')

    if status_filter != 'all':
        suggestions = suggestions.filter(status=status_filter)

    context = {
        'suggestions': suggestions,
        'status_filter': status_filter,
        'statuses': PurchaseSuggestion.STATUS_CHOICES,
    }
    return render(request, 'acquisitions/suggestion_list.html', context)


@login_required
def suggestion_create(request):
    if request.method == 'POST':
        form = PurchaseSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            if hasattr(request.user, 'member_profile'):
                suggestion.member = request.user.member_profile
            suggestion.save()
            messages.success(request, 'Your purchase suggestion has been submitted.')
            return redirect('catalog:book_list')
    else:
        form = PurchaseSuggestionForm()

    return render(request, 'acquisitions/suggestion_form.html', {
        'form': form,
    })


@login_required
@user_passes_test(is_staff)
def suggestion_detail(request, pk):
    suggestion = get_object_or_404(
        PurchaseSuggestion.objects.select_related('member__user', 'reviewed_by'),
        pk=pk,
    )
    return render(request, 'acquisitions/suggestion_detail.html', {
        'suggestion': suggestion,
    })


@login_required
@user_passes_test(is_staff)
@require_POST
def approve_suggestion(request, pk):
    suggestion = get_object_or_404(PurchaseSuggestion, pk=pk)
    suggestion.status = 'approved'
    suggestion.reviewed_by = request.user
    suggestion.review_notes = request.POST.get('review_notes', '')
    suggestion.updated_at = timezone.now()
    suggestion.save()
    messages.success(request, f'Suggestion "{suggestion.title}" has been approved.')
    return redirect('acquisitions:suggestion_list')


@login_required
@user_passes_test(is_staff)
@require_POST
def reject_suggestion(request, pk):
    suggestion = get_object_or_404(PurchaseSuggestion, pk=pk)
    suggestion.status = 'rejected'
    suggestion.reviewed_by = request.user
    suggestion.review_notes = request.POST.get('review_notes', '')
    suggestion.updated_at = timezone.now()
    suggestion.save()
    messages.success(request, f'Suggestion "{suggestion.title}" has been rejected.')
    return redirect('acquisitions:suggestion_list')
