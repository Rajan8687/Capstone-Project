from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, F
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
        
        # Recent activity
        context['recent_activity'] = UserBehavior.objects.select_related('user', 'article').order_by('-timestamp')[:10]
        
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
