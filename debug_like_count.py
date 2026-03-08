#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from articles.models import Article, Like
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== DEBUG LIKE COUNT ===")

# Get a sample article
article = Article.objects.first()
if article:
    print(f"Article: {article.title}")
    print(f"Current likes_count: {article.likes_count}")
    
    # Count actual likes in database
    actual_likes = Like.objects.filter(article=article).count()
    print(f"Actual likes in database: {actual_likes}")
    
    # Show all likes for this article
    likes = Like.objects.filter(article=article)
    for like in likes:
        print(f"  - Liked by: {like.user.username} at {like.created_at}")
    
    # Check if likes_count matches actual count
    if article.likes_count != actual_likes:
        print(f"❌ MISMATCH! likes_count ({article.likes_count}) != actual likes ({actual_likes})")
        # Fix the count
        article.likes_count = actual_likes
        article.save()
        print(f"✅ Fixed! Updated likes_count to {actual_likes}")
    else:
        print(f"✅ Count is correct")
    
    # Test unique constraint
    print("\n=== TESTING UNIQUE CONSTRAINT ===")
    if likes:
        test_user = likes.first().user
        print(f"Testing with user: {test_user.username}")
        
        # Try to create a duplicate like
        try:
            new_like = Like.objects.create(user=test_user, article=article)
            print("❌ ERROR: Duplicate like was created!")
            new_like.delete()
        except Exception as e:
            print(f"✅ Good! Duplicate like prevented: {e}")
else:
    print("No articles found")

print("\n=== CHECKING ALL ARTICLES ===")
for article in Article.objects.all():
    actual_likes = Like.objects.filter(article=article).count()
    if article.likes_count != actual_likes:
        print(f"❌ {article.title}: {article.likes_count} != {actual_likes}")
        article.likes_count = actual_likes
        article.save()
        print(f"  ✅ Fixed to {actual_likes}")
    else:
        print(f"✅ {article.title}: {article.likes_count} likes")
