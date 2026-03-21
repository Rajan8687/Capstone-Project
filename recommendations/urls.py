from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecommendationsView.as_view(), name='recommendations'),
    path('for-you/', views.PersonalizedRecommendationsView.as_view(), name='personalized-recommendations'),
    path('trending/', views.TrendingRecommendationsView.as_view(), name='trending-recommendations'),
    path('similar/<slug:slug>/', views.SimilarArticlesView.as_view(), name='similar-articles'),
    path('feedback/', views.RecommendationFeedbackView.as_view(), name='recommendation-feedback'),
    path('api/recommendations/', views.RecommendationsAPI.as_view(), name='recommendations-api'),
]
