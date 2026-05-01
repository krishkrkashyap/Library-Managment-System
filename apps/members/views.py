from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import MemberProfile, PatronCategory
from .forms import MemberProfileForm, PatronCategoryForm, MemberRegistrationForm

User = get_user_model()


def is_librarian(user):
    return user.is_authenticated and user.is_librarian


@login_required
@user_passes_test(is_librarian)
def member_list(request):
    members = MemberProfile.objects.select_related('user', 'category').all()
    search = request.GET.get('search', '')
    if search:
        members = members.filter(
            user__first_name__icontains=search) | members.filter(user__last_name__icontains=search) | members.filter(membership_id__icontains=search)
    return render(request, 'members/member_list.html', {'members': members, 'search': search})


@login_required
@user_passes_test(is_librarian)
def member_detail(request, pk):
    member = get_object_or_404(MemberProfile, pk=pk)
    borrow_records = member.borrow_records.all()[:20]
    fines = member.fines.all()[:10]
    holds = member.hold_reservations.all()[:10]
    
    context = {
        'member': member,
        'borrow_records': borrow_records,
        'fines': fines,
        'holds': holds,
    }
    return render(request, 'members/member_detail.html', context)


@login_required
@user_passes_test(is_librarian)
def member_create(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    password=form.cleaned_data['password1'],
                    role='member',
                )
                member = form.save(commit=False)
                member.user = user
                member.status = 'active'
                member.save()
            messages.success(request, f'Member {user.get_full_name()} registered successfully!')
            return redirect('members:member_detail', pk=member.pk)
    else:
        form = MemberRegistrationForm()
    return render(request, 'members/member_form.html', {'form': form, 'title': 'Register New Member'})


@login_required
@user_passes_test(is_librarian)
def member_update(request, pk):
    member = get_object_or_404(MemberProfile, pk=pk)
    if request.method == 'POST':
        form = MemberProfileForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('members:member_detail', pk=member.pk)
    else:
        form = MemberProfileForm(instance=member)
    return render(request, 'members/member_form.html', {'form': form, 'title': 'Edit Member', 'member': member})


@login_required
def patron_dashboard(request):
    try:
        member = request.user.member_profile
    except MemberProfile.DoesNotExist:
        messages.error(request, 'No member profile found.')
        return redirect('home')
    
    borrow_records = member.borrow_records.filter(return_date__isnull=True)
    holds = member.hold_reservations.filter(status__in=['pending', 'ready'])
    fines = member.fines.filter(is_paid=False)
    
    context = {
        'member': member,
        'borrow_records': borrow_records,
        'holds': holds,
        'fines': fines,
        'total_fines': member.total_fines,
    }
    return render(request, 'members/patron_dashboard.html', context)


@login_required
@user_passes_test(is_librarian)
def category_list(request):
    categories = PatronCategory.objects.all()
    return render(request, 'members/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_librarian)
def category_create(request):
    if request.method == 'POST':
        form = PatronCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('members:category_list')
    else:
        form = PatronCategoryForm()
    return render(request, 'members/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
@user_passes_test(is_librarian)
def category_update(request, pk):
    category = get_object_or_404(PatronCategory, pk=pk)
    if request.method == 'POST':
        form = PatronCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('members:category_list')
    else:
        form = PatronCategoryForm(instance=category)
    return render(request, 'members/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})
