from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import models
from django.utils import timezone
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
        
        # Always provide both profiles (one will be None)
        context['writer_profile'] = getattr(user, 'writerprofile', None)
        context['reader_profile'] = getattr(user, 'readerprofile', None)
        
        # Add user form for profile editing
        context['user_form'] = UserUpdateForm(instance=user)
        
        if user.is_writer:
            context['user_articles'] = Article.objects.filter(author=user, status='published')[:5]
        
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Always provide both profiles (one will be None)
        writer_profile = getattr(user, 'writerprofile', None)
        reader_profile = getattr(user, 'readerprofile', None)
        context['writer_profile'] = writer_profile
        context['reader_profile'] = reader_profile
        
        # Calculate writer stats for ALL users (including readers who write articles)
        your_articles = Article.objects.filter(author=user)
        published_count = your_articles.filter(status='published').count()
        
        # Calculate stats from articles
        total_views = 0
        total_likes = 0
        for article in your_articles:
            total_views += article.views_count or 0
            total_likes += article.likes_count or 0
        
        # Calculate writer score
        writer_score = 0.0
        if published_count > 0:
            avg_views = total_views / published_count
            avg_likes = total_likes / published_count
            writer_score = (avg_views * 0.6) + (avg_likes * 10 * 0.3) + (published_count * 0.1)
            writer_score = round(writer_score, 2)
        
        # Add stats to context for ALL users
        context['total_published'] = published_count
        context['total_views'] = total_views
        context['total_likes'] = total_likes
        context['writer_score'] = writer_score
        context['all_articles'] = your_articles.order_by('-created_at')  # All articles, not just recent
        
        # Update writer profile if exists
        if writer_profile:
            writer_profile.total_articles_published = published_count
            writer_profile.total_views = total_views
            writer_profile.total_likes = total_likes
            writer_profile.writer_score = writer_score
            writer_profile.save()
        
        # Add recommended articles for all users
        try:
            from recommendations.models import UserRecommendation
            recommended_articles = UserRecommendation.objects.filter(
                user=user,
                expires_at__gt=timezone.now()
            ).select_related('article')[:5]
            context['recommended_articles'] = [rec.article for rec in recommended_articles]
        except Exception:
            # Fallback to popular articles
            context['recommended_articles'] = Article.objects.filter(
                status='published'
            ).order_by('-views_count')[:5]
        
        return context


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            
            # If password was changed, log user out and redirect to login
            if user_form.cleaned_data.get('new_password'):
                messages.info(request, 'Password changed! Please log in with your new password.')
                return redirect('login')
            else:
                return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
    
    # Always provide profile context
    user = request.user
    writer_profile = getattr(user, 'writerprofile', None)
    reader_profile = getattr(user, 'readerprofile', None)
    
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'user': user,
        'writer_profile': writer_profile,
        'reader_profile': reader_profile,
    })
