#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from articles.models import Article
from accounts.models import User

def debug_article_access():
    print("=== Article Access Debug ===")
    
    # Get writer user
    writer_user = User.objects.filter(role='writer').first()
    if not writer_user:
        print("No writer user found!")
        return
        
    print(f"Writer User: {writer_user.username}")
    
    # Get ALL articles by this user
    all_articles = Article.objects.filter(author=writer_user)
    print(f"\nAll articles by {writer_user.username}: {all_articles.count()}")
    
    for article in all_articles:
        print(f"  - {article.title}")
        print(f"    Slug: {article.slug}")
        print(f"    Status: {article.status}")
        print(f"    Author: {article.author.username}")
        print(f"    Is author: {article.author == writer_user}")
        print()
    
    # Test the URL patterns
    print("URLs to test:")
    for article in all_articles:
        print(f"  - /author-article/{article.slug}/")
        print(f"  - /article/{article.slug}/")

if __name__ == '__main__':
    debug_article_access()
