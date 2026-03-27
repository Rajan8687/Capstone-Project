from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from django.db.models import F
from django.urls import reverse_lazy
from .models import Article, Category, Tag, Like, Comment, ReadingSession, ArticleView
from .forms import ArticleForm, CommentForm
from analytics.models import UserBehavior
import json


class HomeView(ListView):
    model = Article
    template_name = 'articles/home.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
        # Limit to 3 articles for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset[:3]
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_articles'] = Article.objects.filter(status='published', is_featured=True)[:3]
        context['trending_articles'] = Article.objects.filter(status='published', is_trending=True)[:5]
        context['categories'] = Category.objects.all()
        return context


class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        return Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['popular_tags'] = Tag.objects.all()[:10]
        
        # Add stats for homepage
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        context['total_articles'] = Article.objects.filter(status='published').count()
        context['total_writers'] = User.objects.filter(role='writer').count()
        context['total_readers'] = User.objects.filter(role='reader').count()
        context['total_likes'] = Article.objects.aggregate(total=models.Sum('likes_count'))['total'] or 0
        
        # Add featured articles
        context['featured_articles'] = Article.objects.filter(
            status='published',
            is_featured=True
        ).select_related('author', 'category').order_by('-created_at')[:6]
        
        # If no featured articles, show recent popular articles
        if not context['featured_articles']:
            context['featured_articles'] = Article.objects.filter(
                status='published'
            ).select_related('author', 'category').order_by('-views_count', '-created_at')[:6]
        
        return context


class UserArticlesView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/user_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        # Show ALL user's articles (draft, published, archived)
        return Article.objects.filter(author=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'My Articles'
        return context


class AuthorArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Allow access to user's own articles regardless of status
        return Article.objects.filter(author=self.request.user).select_related('author', 'category').prefetch_related('tags', 'comments__user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Check if user has already liked this article
        if self.request.user.is_authenticated:
            user_liked = Like.objects.filter(
                user=self.request.user,
                article=article
            ).exists()
            context['user_liked'] = user_liked
        
        # Get comments
        context['comments'] = article.comments.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        """Get article - published for public, any status for author"""
        slug = self.kwargs.get(self.slug_url_kwarg)
        from django.http import Http404
        
        # Try to get published article first (for everyone)
        try:
            return Article.objects.get(slug=slug, status='published')
        except Article.DoesNotExist:
            # If user is authenticated, check if they own the article
            if self.request.user.is_authenticated:
                try:
                    return Article.objects.get(slug=slug, author=self.request.user)
                except Article.DoesNotExist:
                    pass
            # Article not found or not authorized
            raise Http404(f"No article found with slug '{slug}'")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Track article view
        if self.request.user.is_authenticated:
            # Check if user has already viewed this article today
            from django.utils import timezone
            from datetime import timedelta
            
            today = timezone.now().date()
            existing_view = ArticleView.objects.filter(
                user=self.request.user,
                article=article,
                created_at__date=today
            ).exists()
            
            if not existing_view:
                # Create new view record
                ArticleView.objects.create(
                    user=self.request.user,
                    article=article,
                    ip_address=self.get_client_ip(),
                    user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                    referrer=self.request.META.get('HTTP_REFERER', '')
                )
                
                # Update article view count
                Article.objects.filter(pk=article.pk).update(views_count=F('views_count') + 1)
                article.refresh_from_db()
            
            # Track user behavior
            UserBehavior.objects.create(
                user=self.request.user,
                article=article,
                action_type='view',
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
                referrer=self.request.META.get('HTTP_REFERER', '')
            )
            
            # Check if user has already liked this article
            user_liked = Like.objects.filter(
                user=self.request.user,
                article=article
            ).exists()
            context['user_liked'] = user_liked
        
        # Get comments
        context['comments'] = article.comments.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        
        # Get related articles (same category)
        context['related_articles'] = Article.objects.filter(
            category=article.category,
            status='published'
        ).exclude(pk=article.pk)[:3]
        
        # Comment form
        context['comment_form'] = CommentForm()
        
        # Check if user liked this article
        if self.request.user.is_authenticated:
            context['user_liked'] = Like.objects.filter(
                user=self.request.user,
                article=article
            ).exists()
            
            # Get or create reading session for today
            today = timezone.now().date()
            reading_session, created = ReadingSession.objects.get_or_create(
                user=self.request.user,
                article=article,
                start_time__date=today,
                defaults={
                    'start_time': timezone.now(),
                    'time_spent': 0,
                    'scroll_percentage': 0.0,
                    'completed': False
                }
            )
            context['reading_session'] = reading_session
        
        return context

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.author = self.request.user
        # Set published_at if status is published
        if form.cleaned_data['status'] == 'published':
            from django.utils import timezone
            form.instance.published_at = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, 'Article created successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Article'
        return context


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def form_valid(self, form):
        # Set published_at if status is changed to published
        if form.cleaned_data['status'] == 'published' and not self.object.published_at:
            from django.utils import timezone
            form.instance.published_at = timezone.now()
        
        response = super().form_valid(form)
        messages.success(self.request, 'Article updated successfully!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Article: {self.object.title}'
        return context


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'articles/article_confirm_delete.html'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Article deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'articles/category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['articles'] = Article.objects.filter(
            category=category,
            status='published'
        ).select_related('author').prefetch_related('tags')
        return context


class TagDetailView(DetailView):
    model = Tag
    template_name = 'articles/tag_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_object()
        context['articles'] = Article.objects.filter(
            tags=tag,
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')
        return context


class SearchView(ListView):
    model = Article
    template_name = 'articles/search.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__name__icontains=query),
                status='published'
            ).distinct().select_related('author', 'category').prefetch_related('tags')
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class LikeArticleView(LoginRequiredMixin, View):
    def post(self, request, slug):
        try:
            article = get_object_or_404(Article, slug=slug, status='published')
            user = request.user
            
            # Use atomic transaction to prevent race conditions
            from django.db import transaction
            
            with transaction.atomic():
                # Try to get existing like
                try:
                    existing_like = Like.objects.select_for_update().get(user=user, article=article)
                    # Like exists, so delete it (unlike)
                    existing_like.delete()
                    liked = False
                except Like.DoesNotExist:
                    # No existing like, create new one
                    Like.objects.create(user=user, article=article)
                    liked = True
                    
                    # Track user behavior only for new likes
                    UserBehavior.objects.create(
                        user=user,
                        article=article,
                        action_type='like',
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
            
            # Get the actual count after transaction
            actual_count = Like.objects.filter(article=article).count()
            
            # Update article
            article.likes_count = actual_count
            article.save(update_fields=['likes_count'])
            
            return JsonResponse({
                'success': True,
                'liked': liked,
                'likes_count': actual_count
            })
            
        except Article.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Article not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AddCommentView(LoginRequiredMixin, DetailView):
    model = Article
    slug_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.save()
            
            # Update comment count
            Article.objects.filter(pk=article.pk).update(comments_count=F('comments_count') + 1)
            
            # Track user behavior
            UserBehavior.objects.create(
                user=request.user,
                article=article,
                action_type='comment',
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment. Please try again.')
        
        return redirect('article-detail', slug=article.slug)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@require_POST
def track_reading_session(request, slug):
    """Track reading session for analytics"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'})
    
    try:
        article = get_object_or_404(Article, slug=slug)
        data = json.loads(request.body)
        
        session = ReadingSession.objects.create(
            user=request.user,
            article=article,
            start_time=timezone.now(),
            scroll_percentage=data.get('scroll_percentage', 0.0),
            completed=data.get('completed', False)
        )
        
        return JsonResponse({'status': 'success', 'session_id': session.id})
    
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data format'})


@require_POST
def update_reading_session(request, session_id):
    """Update reading session when user finishes reading"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'})
    
    try:
        session = get_object_or_404(ReadingSession, id=session_id, user=request.user)
        data = json.loads(request.body)
        
        session.end_time = timezone.now()
        session.scroll_percentage = data.get('scroll_percentage', session.scroll_percentage)
        session.completed = data.get('completed', session.completed)
        session.calculate_time_spent()
        
        return JsonResponse({'status': 'success', 'time_spent': session.time_spent})
    
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data format'})


class EditCommentView(LoginRequiredMixin, View):
    """Edit a comment"""
    def post(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            data = json.loads(request.body)
            new_content = data.get('content', '').strip()
            
            if not new_content:
                return JsonResponse({'success': False, 'error': 'Content cannot be empty'})
            
            comment.content = new_content
            comment.save()
            
            return JsonResponse({'success': True, 'content': comment.content})
        
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comment not found'})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'success': False, 'error': 'Invalid data format'})


class DeleteCommentView(LoginRequiredMixin, View):
    """Delete a comment"""
    def post(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            comment.delete()
            
            return JsonResponse({'success': True})
        
        except Comment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comment not found'})


class TrackReadingTimeView(LoginRequiredMixin, View):
    """Track user reading time and scroll percentage"""
    def post(self, request, slug):
        try:
            article = get_object_or_404(Article, slug=slug)
            data = json.loads(request.body)
            
            time_spent = data.get('time_spent', 0)  # in seconds
            scroll_percentage = data.get('scroll_percentage', 0.0)
            completed = data.get('completed', False)
            
            # Get or create reading session for today
            today = timezone.now().date()
            session, created = ReadingSession.objects.get_or_create(
                user=request.user,
                article=article,
                start_time__date=today,
                defaults={
                    'start_time': timezone.now(),
                    'time_spent': 0,
                    'scroll_percentage': 0.0,
                    'completed': False
                }
            )
            
            # Update session data
            session.time_spent = time_spent
            session.scroll_percentage = scroll_percentage
            session.completed = completed
            session.end_time = timezone.now()
            session.save()
            
            return JsonResponse({
                'success': True,
                'time_spent': session.time_spent,
                'scroll_percentage': session.scroll_percentage,
                'completed': session.completed
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
