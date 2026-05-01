from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.notifications.models import Notification


@login_required
def notification_list(request):
    try:
        member = request.user.member_profile
        notifications = Notification.objects.filter(member=member)
    except Exception:
        notifications = Notification.objects.none()
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications.order_by('-created_at')[:50],
        'unread_count': unread_count,
    })


@login_required
@require_POST
def mark_as_read(request, notification_id):
    try:
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            member=request.user.member_profile,
        )
        notification.mark_as_read()
        messages.success(request, 'Notification marked as read.')
    except Exception:
        pass

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


@login_required
@require_POST
def mark_all_read(request):
    try:
        Notification.objects.filter(
            member=request.user.member_profile,
            is_read=False,
        ).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
    except Exception:
        pass

    return redirect('notifications:notification_list')
