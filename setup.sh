#!/bin/bash

echo "🚀 Setting up InsightWrite - Data-Driven Article Platform"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (new syntax)
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your settings."
fi

# Build and start containers
echo "🐳 Building Docker containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🗄️ Running database migrations..."
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@insightwrite.com', 'admin123')
    print('✅ Superuser created: admin/admin123')
else:
    print('ℹ️ Superuser already exists')
"

# Collect static files
echo "📁 Collecting static files..."
docker compose exec web python manage.py collectstatic --noinput

# Load sample data
echo "📊 Loading sample data..."
docker compose exec web python manage.py shell -c "
from articles.models import Category, Tag, Article
from accounts.models import User, WriterProfile
from django.utils.text import slugify
import random

# Create categories
categories_data = [
    'Data Science', 'Machine Learning', 'Web Development', 'Python', 
    'JavaScript', 'Django', 'React', 'Analytics', 'AI', 'Cloud Computing'
]

for cat_name in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': slugify(cat_name)}
    )
    if created:
        print(f'✅ Created category: {cat_name}')

# Create tags
tags_data = [
    'python', 'django', 'react', 'machine-learning', 'data-science',
    'javascript', 'web-development', 'analytics', 'ai', 'cloud'
]

for tag_name in tags_data:
    tag, created = Tag.objects.get_or_create(
        name=tag_name,
        defaults={'slug': slugify(tag_name)}
    )
    if created:
        print(f'✅ Created tag: {tag_name}')

# Create sample writer
writer_user, created = User.objects.get_or_create(
    username='writer',
    defaults={
        'email': 'writer@insightwrite.com',
        'role': 'writer',
        'bio': 'Professional tech writer and data scientist'
    }
)
if created:
    writer_user.set_password('writer123')
    writer_user.save()
    WriterProfile.objects.create(user=writer_user)
    print('✅ Created sample writer: writer/writer123')

# Create sample articles
categories = list(Category.objects.all())
tags = list(Tag.objects.all())

if categories and tags:
    sample_articles = [
        {
            'title': 'Getting Started with Machine Learning in Python',
            'content': '''Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. In this comprehensive guide, we'll explore the fundamentals of machine learning using Python, one of the most popular programming languages for data science.

We'll cover key concepts including supervised learning, unsupervised learning, and reinforcement learning. You'll learn how to implement basic algorithms using popular libraries like scikit-learn, TensorFlow, and PyTorch.

By the end of this article, you'll have a solid understanding of machine learning concepts and be ready to build your first ML models.''',
            'excerpt': 'Learn the fundamentals of machine learning using Python. This comprehensive guide covers supervised, unsupervised, and reinforcement learning.',
            'category': random.choice(categories)
        },
        {
            'title': 'Building Modern Web Applications with Django and React',
            'content': '''Django and React form a powerful combination for building modern web applications. Django provides a robust backend framework with built-in authentication, admin interface, and ORM, while React offers a flexible frontend library for building interactive user interfaces.

In this tutorial, we'll walk through creating a full-stack application from scratch. You'll learn how to set up a Django REST API, implement JWT authentication, and create a responsive React frontend.

We'll cover best practices for API design, state management, component architecture, and deployment strategies. By the end, you'll have a production-ready web application.''',
            'excerpt': 'Learn how to build full-stack web applications using Django and React. Complete tutorial with API design and frontend development.',
            'category': random.choice(categories)
        },
        {
            'title': 'Data Visualization Techniques for Better Insights',
            'content': '''Effective data visualization is crucial for communicating insights and making data-driven decisions. This article explores various visualization techniques and tools that can help you present data in meaningful ways.

We'll discuss different chart types and when to use them, color theory in data visualization, interactive visualizations, and best practices for creating clear and impactful visualizations.

You'll learn how to use popular libraries like Matplotlib, Seaborn, Plotly, and D3.js to create stunning visualizations that tell compelling data stories.''',
            'excerpt': 'Master data visualization techniques to communicate insights effectively. Learn about chart types, color theory, and popular visualization libraries.',
            'category': random.choice(categories)
        }
    ]
    
    for article_data in sample_articles:
        article, created = Article.objects.get_or_create(
            title=article_data['title'],
            defaults={
                'slug': slugify(article_data['title']),
                'author': writer_user,
                'category': article_data['category'],
                'content': article_data['content'],
                'excerpt': article_data['excerpt'],
                'status': 'published',
                'reading_time': len(article_data['content'].split()) // 200
            }
        )
        if created:
            # Add random tags
            article.tags.set(random.sample(tags, min(3, len(tags))))
            print(f'✅ Created article: {article.title}')

print('🎉 Sample data loaded successfully!')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Access your application:"
echo "   🌐 Web App: http://localhost:8000"
echo "   🔧 Admin: http://localhost:8000/admin"
echo "   📊 Analytics: http://localhost:8000/analytics/"
echo ""
echo "👤 Login credentials:"
echo "   Admin: admin/admin123"
echo "   Writer: writer/writer123"
echo ""
echo "🚀 Your InsightWrite platform is ready to use!"
