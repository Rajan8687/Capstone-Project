#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from articles.models import Article, Like
from accounts.models import User

def debug_like_simple():
    print("=== Simple Like Debug ===")
    
    # Get a writer user
    writer = User.objects.filter(role='writer').first()
    if not writer:
        print("No writer user found!")
        return
        
    print(f"Writer: {writer.username} (ID: {writer.id})")
    
    # Get a published article
    article = Article.objects.filter(status='published').first()
    if not article:
        print("No published articles found!")
        return
        
    print(f"Article: {article.title} (ID: {article.id}, slug: {article.slug})")
    print(f"Current likes: {article.likes_count}")
    
    # Check existing likes
    existing_likes = Like.objects.filter(article=article).count()
    print(f"Total likes in database: {existing_likes}")
    
    # User's existing like
    user_like = Like.objects.filter(user=writer, article=article).first()
    print(f"User's like: {user_like}")
    
    # Test the URL
    try:
        like_url = reverse('like-article', kwargs={'slug': article.slug})
        print(f"Like URL: {like_url}")
        
        # Test with Django client
        client = Client()
        client.force_login(writer)
        
        response = client.post(like_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        print(f"Response status: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        
        # Check database after request
        article.refresh_from_db()
        print(f"Article likes after: {article.likes_count}")
        
        # Check if like was created/deleted
        new_user_like = Like.objects.filter(user=writer, article=article).first()
        print(f"User's like after: {new_user_like}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_like_simple()
