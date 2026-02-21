#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone_project.settings')
django.setup()

from articles.models import Category, Tag

def create_basic_data():
    print("Creating basic categories and tags...")
    
    # Create categories
    categories = [
        'Technology',
        'Programming',
        'Web Development',
        'Data Science',
        'Machine Learning',
        'Business',
        'Marketing',
        'Design',
        'Lifestyle',
        'Education'
    ]
    
    for cat_name in categories:
        category, created = Category.objects.get_or_create(
            name=cat_name,
            defaults={'slug': cat_name.lower().replace(' ', '-')}
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")
    
    # Create tags
    tags = [
        'python',
        'django',
        'javascript',
        'react',
        'html',
        'css',
        'sql',
        'machine learning',
        'ai',
        'web development',
        'tutorial',
        'beginner',
        'advanced',
        'tips',
        'best practices',
        'coding'
    ]
    
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': tag_name.lower().replace(' ', '-')}
        )
        if created:
            print(f"Created tag: {tag.name}")
        else:
            print(f"Tag already exists: {tag.name}")
    
    print("\nBasic data creation completed!")
    print(f"Total categories: {Category.objects.count()}")
    print(f"Total tags: {Tag.objects.count()}")

if __name__ == '__main__':
    create_basic_data()
