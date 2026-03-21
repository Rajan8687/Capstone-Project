from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, F, Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from articles.models import Article, Category, Like, Comment
from .models import UserBehavior, ReadingPattern, TrendingScore, ContentPerformance
import pandas as pd
import plotly.graph_objs as go
import plotly.utils

User = get_user_model()


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic stats
        context['total_articles'] = Article.objects.filter(status='published').count()
        context['total_users'] = UserBehavior.objects.values('user').distinct().count()
        context['total_views'] = Article.objects.aggregate(total=Count('article_views'))['total'] or 0
        context['total_likes'] = Like.objects.count()
        context['total_comments'] = Comment.objects.count()
        
        # Top categories
        context['top_categories'] = Category.objects.annotate(
            article_count=Count('articles', filter=Q(articles__status='published'))
        ).order_by('-article_count')[:5]
        
        # Recent activity - renamed to match template
        context['recent_activity'] = UserBehavior.objects.select_related('user', 'article').order_by('-timestamp')[:10]
        context['recent_behaviors'] = context['recent_activity']  # Alias for template compatibility
        
        # Trending articles - calculate dynamically if TrendingScore doesn't exist
        trending_scores = TrendingScore.objects.select_related('article').filter(
            article__status='published'
        ).order_by('-score')[:10]
        
        if trending_scores.exists():
            context['trending_articles'] = [ts.article for ts in trending_scores]
            context['trending_scores'] = {ts.article.id: ts.score for ts in trending_scores}
        else:
            # Fallback: calculate trending based on views and engagement
            from django.db.models import F, ExpressionWrapper, FloatField
            trending_articles = Article.objects.filter(
                status='published',
                views_count__gt=0
            ).annotate(
                engagement_score=ExpressionWrapper(
                    (F('likes_count') + F('comments_count')) * 1.0 / F('views_count'),
                    output_field=FloatField()
                )
            ).order_by('-views_count', '-engagement_score')[:10]
            
            context['trending_articles'] = trending_articles
            # Create mock scores based on views
            context['trending_scores'] = {a.id: a.views_count * 0.1 + a.likes_count for a in trending_articles}
        
        # Top writers - calculate dynamically
        top_writers = User.objects.filter(
            role='writer'
        ).select_related('writerprofile').order_by('-writerprofile__writer_score')[:10]
        
        if not top_writers.exists():
            # Fallback: get all users who have published articles
            top_writers = User.objects.filter(
                articles__status='published'
            ).annotate(
                total_articles=Count('articles', filter=Q(articles__status='published')),
                total_views=Sum('articles__views_count'),
                total_likes=Sum('articles__likes_count')
            ).filter(total_articles__gt=0).order_by('-total_views')[:10]
            
            # Create mock writer profiles for display
            for writer in top_writers:
                if not hasattr(writer, 'writerprofile'):
                    writer.writerprofile = None
                    writer.mock_score = (writer.total_views or 0) * 0.01 + (writer.total_likes or 0) * 0.1
                    writer.total_articles_published = writer.total_articles
        
        context['top_writers'] = top_writers
        
        # Top performing articles - add missing context
        context['top_performing'] = Article.objects.filter(
            status='published'
        ).order_by('-views_count')[:10]
        
        # Chart data - add missing chart data
        import json
        from datetime import datetime, timedelta
        
        # Views chart data (last 30 days)
        last_30_days = timezone.now() - timedelta(days=30)
        articles_by_date = Article.objects.filter(
            created_at__gte=last_30_days
        ).extra(select={'date': 'DATE(created_at)'}).values('date').annotate(count=Count('id'))
        
        dates = []
        counts = []
        for item in articles_by_date:
            dates.append(str(item['date']))
            counts.append(item['count'])
        
        context['views_chart_data'] = json.dumps({'dates': dates, 'views': counts})
        
        # Category chart data
        categories = Category.objects.annotate(
            count=Count('articles', filter=Q(articles__status='published'))
        ).filter(count__gt=0)[:10]
        
        context['category_chart_data'] = json.dumps({
            'categories': [c.name for c in categories],
            'counts': [c.count for c in categories]
        })
        
        # Reading patterns data
        context['reading_patterns_data'] = json.dumps({
            'hours': list(range(24)),
            'reading_time': [0] * 24  # Placeholder data
        })
        
        return context


class ReaderBehaviorView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/reader_behavior.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Reading patterns by category
        category_stats = ReadingPattern.objects.values('category__name').annotate(
            total_articles=Count('total_articles_read'),
            avg_time=Avg('total_time_spent'),
            completion_rate=Avg('completion_rate')
        ).order_by('-total_articles')
        
        context['category_stats'] = category_stats
        
        # User behavior timeline
        last_30_days = timezone.now() - timedelta(days=30)
        behavior_timeline = UserBehavior.objects.filter(
            timestamp__gte=last_30_days
        ).extra(
            select={'day': 'date(timestamp)'}
        ).values('day', 'action_type').annotate(count=Count('id')).order_by('day')
        
        context['behavior_timeline'] = behavior_timeline
        
        return context


class ContentPerformanceView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/content_performance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Top performing articles
        context['top_articles'] = Article.objects.filter(status='published').annotate(
            engagement_rate=F('likes_count') + F('comments_count')
        ).order_by('-engagement_rate')[:10]
        
        # Performance by category
        context['category_performance'] = Category.objects.annotate(
            total_views=Count('articles__article_views'),
            total_likes=Count('articles__likes'),
            total_comments=Count('articles__comments')
        ).order_by('-total_views')
        
        return context


class TrendingPredictionView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/trending_prediction.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Current trending articles
        context['trending_articles'] = TrendingScore.objects.select_related('article').order_by('-score')[:10]
        
        # Recent predictions
        from recommendations.models import TrendingPrediction
        context['recent_predictions'] = TrendingPrediction.objects.select_related('article').order_by('-prediction_date')[:10]
        
        return context


class ReadingPatternsAPI(LoginRequiredMixin, TemplateView):
    """API endpoint for reading patterns data"""
    
    def get(self, request, *args, **kwargs):
        # Get reading patterns data
        patterns = ReadingPattern.objects.values('category__name').annotate(
            total_articles=Count('total_articles_read'),
            avg_time=Avg('total_time_spent')
        ).order_by('-total_articles')
        
        data = {
            'categories': [p['category__name'] for p in patterns],
            'articles_read': [p['total_articles'] for p in patterns],
            'avg_time': [p['avg_time'] or 0 for p in patterns]
        }
        
        return JsonResponse(data)


class ContentStatsAPI(LoginRequiredMixin, TemplateView):
    """API endpoint for content statistics"""
    
    def get(self, request, *args, **kwargs):
        # Get content performance data
        last_7_days = timezone.now() - timedelta(days=7)
        
        daily_stats = ContentPerformance.objects.filter(
            date__gte=last_7_days
        ).values('date').annotate(
            total_views=Count('daily_views'),
            total_likes=Count('daily_likes'),
            total_comments=Count('daily_comments')
        ).order_by('date')
        
        data = {
            'dates': [str(s['date']) for s in daily_stats],
            'views': [s['total_views'] for s in daily_stats],
            'likes': [s['total_likes'] for s in daily_stats],
            'comments': [s['total_comments'] for s in daily_stats]
        }
        
        return JsonResponse(data)
