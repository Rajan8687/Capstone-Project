from django.urls import path
from . import api_views

urlpatterns = [
    path('articles/', api_views.ArticleListAPIView.as_view(), name='article-list-api'),
    path('articles/<slug:slug>/', api_views.ArticleDetailAPIView.as_view(), name='article-detail-api'),
    path('categories/', api_views.CategoryListAPIView.as_view(), name='category-list-api'),
    path('tags/', api_views.TagListAPIView.as_view(), name='tag-list-api'),
    path('recommendations/', api_views.RecommendationAPIView, name='recommendation-api'),
]
