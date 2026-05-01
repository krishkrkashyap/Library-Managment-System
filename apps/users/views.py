from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})
