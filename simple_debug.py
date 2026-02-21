#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from articles.models import Article
from accounts.models import User

def simple_debug():
    print("=== Simple Article Count Debug ===")
    
    # Get writer user
    writer_user = User.objects.filter(role='writer').first()
    if not writer_user:
        print("No writer user found!")
        return
        
    print(f"Writer User: {writer_user.username}")
    
    # Check ALL articles by this user
    all_articles = Article.objects.filter(author=writer_user)
    print(f"\nALL articles by {writer_user.username}: {all_articles.count()}")
    
    # Check articles by status
    published = all_articles.filter(status='published')
    draft = all_articles.filter(status='draft')
    archived = all_articles.filter(status='archived')
    
    print(f"Published: {published.count()}")
    print(f"Draft: {draft.count()}")
    print(f"Archived: {archived.count()}")
    
    print(f"\nTotal: {published.count() + draft.count() + archived.count()}")
    
    # Show each article
    print("\nAll Articles:")
    for article in all_articles:
        print(f"  - {article.title}")
        print(f"    Status: {article.status}")
        print(f"    Views: {article.views_count}")
        print(f"    Likes: {article.likes_count}")
        print()

if __name__ == '__main__':
    simple_debug()
