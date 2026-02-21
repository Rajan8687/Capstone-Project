#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from articles.models import Article, Like
from accounts.models import User

def test_like_functionality():
    print("=== Like Functionality Test ===")
    
    # Get writer user
    writer_user = User.objects.filter(role='writer').first()
    if not writer_user:
        print("No writer user found!")
        return
        
    print(f"Writer User: {writer_user.username}")
    
    # Get an article
    article = Article.objects.filter(author=writer_user).first()
    if not article:
        print("No articles found!")
        return
        
    print(f"Article: {article.title} (slug: {article.slug})")
    print(f"Current likes: {article.likes_count}")
    
    # Check if user already liked
    existing_like = Like.objects.filter(user=writer_user, article=article).exists()
    print(f"User already liked: {existing_like}")
    
    # Test like creation
    like, created = Like.objects.get_or_create(
        user=writer_user,
        article=article
    )
    
    print(f"Like created: {created}")
    print(f"New likes count: {article.likes_count}")
    
    # Test unlike
    if not created:
        like.delete()
        Article.objects.filter(pk=article.pk).update(likes_count=F('likes_count') - 1)
        article.refresh_from_db()
        print(f"After unlike: {article.likes_count}")
    else:
        Article.objects.filter(pk=article.pk).update(likes_count=F('likes_count') + 1)
        article.refresh_from_db()
        print(f"After like: {article.likes_count}")

if __name__ == '__main__':
    test_like_functionality()
