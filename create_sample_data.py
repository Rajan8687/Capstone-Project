#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
django.setup()

from django.contrib.auth.models import User
from articles.models import Article, Category, Tag

def create_sample_data():
    print("Creating sample data...")
    
    # Get or create users
    admin_user = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})[0]
    writer_user = User.objects.get_or_create(username='writer', defaults={'email': 'writer@example.com'})[0]
    
    # Create categories
    tech_cat = Category.objects.get_or_create(name='Technology', defaults={'slug': 'technology'})[0]
    business_cat = Category.objects.get_or_create(name='Business', defaults={'slug': 'business'})[0]
    science_cat = Category.objects.get_or_create(name='Science', defaults={'slug': 'science'})[0]
    
    # Create tags
    ai_tag = Tag.objects.get_or_create(name='Artificial Intelligence', defaults={'slug': 'artificial-intelligence'})[0]
    python_tag = Tag.objects.get_or_create(name='Python', defaults={'slug': 'python'})[0]
    startup_tag = Tag.objects.get_or_create(name='Startup', defaults={'slug': 'startup'})[0]
    ml_tag = Tag.objects.get_or_create(name='Machine Learning', defaults={'slug': 'machine-learning'})[0]
    
    # Create sample articles
    articles_data = [
        {
            'title': 'Getting Started with Django',
            'slug': 'getting-started-with-django',
            'excerpt': 'Learn how to build web applications with Django framework.',
            'content': '''Django is a powerful web framework that makes it easy to build web applications. In this article, we'll explore the basics of Django and how you can get started building your first web application.

Django follows the Model-View-Template (MVT) pattern and provides many built-in features that make web development faster and more efficient.

Let's start by understanding the key components of Django and how they work together to create amazing web applications.''',
            'author': admin_user,
            'category': tech_cat,
            'tags': [python_tag],
            'reading_time': 5
        },
        {
            'title': 'Machine Learning Basics',
            'slug': 'machine-learning-basics',
            'excerpt': 'An introduction to machine learning concepts and applications.',
            'content': '''Machine learning is revolutionizing the way we interact with technology. From recommendation systems to self-driving cars, ML is everywhere.

In this comprehensive guide, we'll explore the fundamental concepts of machine learning, including supervised learning, unsupervised learning, and reinforcement learning.

We'll also look at popular ML frameworks like TensorFlow and PyTorch, and discuss real-world applications of machine learning in various industries.''',
            'author': writer_user,
            'category': science_cat,
            'tags': [ml_tag, ai_tag],
            'reading_time': 8
        },
        {
            'title': 'Building a Successful Startup',
            'slug': 'building-successful-startup',
            'excerpt': 'Key strategies for launching and growing a successful startup.',
            'content': '''Starting a successful startup requires more than just a great idea. It needs proper planning, execution, and the right team.

This article covers essential aspects of startup building including:
- Market research and validation
- Building a minimum viable product
- Funding strategies
- Team building
- Growth hacking techniques

Learn from successful entrepreneurs and avoid common pitfalls that many startups face.''',
            'author': admin_user,
            'category': business_cat,
            'tags': [startup_tag],
            'reading_time': 6
        }
    ]
    
    for article_data in articles_data:
        article, created = Article.objects.get_or_create(
            slug=article_data['slug'],
            defaults=article_data
        )
        if created:
            # Add tags
            article.tags.set(article_data['tags'])
            article.status = 'published'
            article.save()
            print(f"Created article: {article.title}")
        else:
            print(f"Article already exists: {article.title}")
    
    print(f"\nTotal articles created: {Article.objects.count()}")
    print("\nSample articles available:")
    for article in Article.objects.all():
        print(f"- {article.title} (slug: {article.slug})")

if __name__ == '__main__':
    create_sample_data()
