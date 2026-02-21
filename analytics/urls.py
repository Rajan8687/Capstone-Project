from django.urls import path
from . import views

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
    path('reader-behavior/', views.ReaderBehaviorView.as_view(), name='reader-behavior'),
    path('content-performance/', views.ContentPerformanceView.as_view(), name='content-performance'),
    path('trending-prediction/', views.TrendingPredictionView.as_view(), name='trending-prediction'),
    path('api/reading-patterns/', views.ReadingPatternsAPI.as_view(), name='reading-patterns-api'),
    path('api/content-stats/', views.ContentStatsAPI.as_view(), name='content-stats-api'),
]
