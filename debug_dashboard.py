#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone_project.settings')
django.setup()

from articles.models import Article
from accounts.models import User, WriterProfile

def debug_dashboard():
    print("=== Dashboard Debug ===")
    
    # Get a sample writer user
    try:
        writer_user = User.objects.filter(role='writer').first()
        if not writer_user:
            print("No writer user found!")
            return
            
        print(f"Writer User: {writer_user.username}")
        
        # Get writer profile
        writer_profile = getattr(writer_user, 'writerprofile', None)
        print(f"Writer Profile: {writer_profile}")
        
        # Get all articles
        user_articles = Article.objects.filter(author=writer_user)
        print(f"All Articles Count: {user_articles.count()}")
        
        # Get published articles
        published_articles = user_articles.filter(status='published')
        print(f"Published Articles Count: {published_articles.count()}")
        
        # Show article details
        for article in user_articles:
            print(f"  - {article.title} (status: {article.status})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_dashboard()
