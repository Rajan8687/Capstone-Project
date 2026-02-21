from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import models
from .forms import CustomUserCreationForm, UserUpdateForm, ReaderProfileForm, WriterProfileForm
from .models import User, ReaderProfile, WriterProfile
from articles.models import Article


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create appropriate profile based on role
        if form.cleaned_data['role'] == 'reader':
            ReaderProfile.objects.create(user=self.object)
        elif form.cleaned_data['role'] == 'writer':
            WriterProfile.objects.create(user=self.object)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        if user.is_writer:
            context['writer_profile'] = getattr(user, 'writerprofile', None)
            context['user_articles'] = Article.objects.filter(author=user, status='published')[:5]
        else:
            context['reader_profile'] = getattr(user, 'readerprofile', None)
        
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_writer:
            writer_profile = getattr(user, 'writerprofile', None)
            
            # Get ALL YOUR articles (regardless of status)
            your_articles = Article.objects.filter(author=user)
            
            # Calculate stats for ALL articles
            total_articles = your_articles.count()
            
            # Manual calculation for ALL articles
            total_views = 0
            total_likes = 0
            for article in your_articles:
                total_views += article.views_count or 0
                total_likes += article.likes_count or 0
            
            # Also get published count for reference
            published_count = your_articles.filter(status='published').count()
            
            # Update writer profile
            if writer_profile:
                writer_profile.total_articles_published = published_count
                writer_profile.total_views = total_views
                writer_profile.total_likes = total_likes
                writer_profile.calculate_writer_score()
            
            context['writer_profile'] = writer_profile
            context['recent_articles'] = your_articles.order_by('-created_at')[:5]
            context['total_published'] = total_articles  # Show ALL articles count
            context['total_views'] = total_views
            context['total_likes'] = total_likes
            context['published_count'] = published_count  # For reference
        else:
            reader_profile = getattr(user, 'readerprofile', None)
            context['reader_profile'] = reader_profile
            
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_form = UserUpdateForm(instance=self.request.user)
        context['user_form'] = user_form
        return context


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
    })
