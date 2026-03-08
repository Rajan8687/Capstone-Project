#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from articles.models import Article, Category, Tag
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

print("=== Creating Sample Articles ===")

# Get or create categories
categories_data = [
    ('Technology', 'technology'),
    ('Data Science', 'data-science'),
    ('Web Development', 'web-development'),
    ('Machine Learning', 'machine-learning'),
    ('Python Programming', 'python-programming')
]

categories = []
for name, slug in categories_data:
    cat, created = Category.objects.get_or_create(
        name=name,
        defaults={'slug': slug}
    )
    categories.append(cat)
    print(f"{'Created' if created else 'Found'} category: {name}")

# Get a writer user
writer = User.objects.filter(role='writer').first()
if not writer:
    writer = User.objects.first()

if writer:
    print(f"Using writer: {writer.username}")
    
    # Sample articles
    articles_data = [
        {
            'title': 'Getting Started with Django Web Development',
            'content': '''Django is a powerful web framework that makes it easy to build web applications. In this comprehensive guide, we'll cover everything you need to know to get started with Django development.

From setting up your first project to deploying your application, this article will walk you through the entire process. We'll cover models, views, templates, and the Django admin interface.

By the end of this article, you'll have a solid understanding of Django fundamentals and be ready to build your own web applications.''',
            'excerpt': 'Learn the basics of Django web development from scratch',
            'category': categories[0]  # Technology
        },
        {
            'title': 'Introduction to Data Science with Python',
            'content': '''Data science is one of the most exciting fields in technology today. This article introduces you to the fundamental concepts of data science using Python.

We'll explore data analysis, visualization, and machine learning basics. You'll learn about popular libraries like pandas, numpy, matplotlib, and scikit-learn.

Whether you're a beginner or have some programming experience, this guide will help you understand the data science workflow and start your journey into this fascinating field.''',
            'excerpt': 'Explore the fundamentals of data science using Python',
            'category': categories[1]  # Data Science
        },
        {
            'title': 'Building REST APIs with Django REST Framework',
            'content': '''REST APIs are essential for modern web applications. Django REST Framework (DRF) makes it easy to build powerful APIs with Django.

In this tutorial, we'll cover how to create serializers, views, and URLs for your API. We'll also explore authentication, permissions, and documentation.

You'll learn best practices for API design and how to create endpoints that are both powerful and easy to use.''',
            'excerpt': 'Learn how to build professional REST APIs using Django REST Framework',
            'category': categories[2]  # Web Development
        },
        {
            'title': 'Machine Learning Fundamentals',
            'content': '''Machine learning is revolutionizing how we solve complex problems. This article covers the fundamental concepts you need to understand to get started with ML.

We'll explore supervised and unsupervised learning, neural networks, and deep learning basics. You'll learn about common algorithms and when to use them.

This guide provides a solid foundation for anyone interested in machine learning, whether you're a developer, data scientist, or just curious about AI.''',
            'excerpt': 'A comprehensive introduction to machine learning concepts and algorithms',
            'category': categories[3]  # Machine Learning
        },
        {
            'title': 'Advanced Python Programming Techniques',
            'content': '''Take your Python skills to the next level with advanced programming techniques. This article covers decorators, generators, context managers, and metaclasses.

We'll explore Python's advanced features and how to use them effectively in your projects. You'll learn about performance optimization and best practices for writing clean, efficient code.

Whether you're building web applications, data science projects, or automation scripts, these techniques will make you a more effective Python developer.''',
            'excerpt': 'Master advanced Python programming techniques and best practices',
            'category': categories[4]  # Python Programming
        }
    ]
    
    created_count = 0
    for article_data in articles_data:
        # Check if article already exists
        existing = Article.objects.filter(title=article_data['title']).first()
        if not existing:
            article = Article.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                excerpt=article_data['excerpt'],
                author=writer,
                category=article_data['category'],
                status='published',
                slug=slugify(article_data['title']),
                views_count=50 + (created_count * 20),
                likes_count=5 + created_count
            )
            created_count += 1
            print(f"Created article: {article.title}")
        else:
            print(f"Article already exists: {existing.title}")
    
    print(f"\n✅ Created {created_count} sample articles!")
    print(f"Total published articles: {Article.objects.filter(status='published').count()}")
else:
    print("❌ No writer user found!")

print("\n=== Article Creation Complete ===")
