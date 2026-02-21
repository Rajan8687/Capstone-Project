#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from articles.models import Article
from accounts.models import User

def debug_article_counting():
    print("=== Article Counting Debug ===")
    
    # Get writer user
    writer_user = User.objects.filter(role='writer').first()
    if not writer_user:
        print("No writer user found!")
        return
        
    print(f"Writer User: {writer_user.username}")
    
    # Check all articles by this user
    all_user_articles = Article.objects.filter(author=writer_user)
    print(f"All articles by {writer_user.username}: {all_user_articles.count()}")
    
    # Check published articles by this user
    published_articles = all_user_articles.filter(status='published')
    print(f"Published articles by {writer_user.username}: {published_articles.count()}")
    
    # Show each article with status
    print("\nArticle Details:")
    for article in all_user_articles:
        print(f"  - {article.title} (status: {article.status}, views: {article.views_count}, likes: {article.likes_count})")
    
    # Calculate totals manually
    total_views = sum(article.views_count for article in published_articles)
    total_likes = sum(article.likes_count for article in published_articles)
    
    print(f"\nManual Calculation:")
    print(f"  - Total Views: {total_views}")
    print(f"  - Total Likes: {total_likes}")
    
    # Check Django aggregate
    from django.db.models import Sum
    agg_views = published_articles.aggregate(total=Sum('views_count'))['total'] or 0
    agg_likes = published_articles.aggregate(total=Sum('likes_count'))['total'] or 0
    
    print(f"\nDjango Aggregate:")
    print(f"  - Total Views: {agg_views}")
    print(f"  - Total Likes: {agg_likes}")

if __name__ == '__main__':
    debug_article_counting()
