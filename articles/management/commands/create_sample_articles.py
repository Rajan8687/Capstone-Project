from django.core.management.base import BaseCommand
from accounts.models import User
from articles.models import Article, Category, Tag

class Command(BaseCommand):
    help = 'Create sample articles for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample articles...')
        
        # Get users
        try:
            admin_user = User.objects.get(username='admin')
            writer_user = User.objects.get(username='writer')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Users not found. Please create admin and writer users first.'))
            return
        
        # Create categories
        tech_cat, _ = Category.objects.get_or_create(name='Technology', defaults={'slug': 'technology'})
        business_cat, _ = Category.objects.get_or_create(name='Business', defaults={'slug': 'business'})
        science_cat, _ = Category.objects.get_or_create(name='Science', defaults={'slug': 'science'})
        
        # Handle existing tags properly
        python_tag = Tag.objects.filter(slug='python').first()
        if not python_tag:
            python_tag = Tag.objects.create(name='Python', slug='python')
        
        ai_tag = Tag.objects.filter(slug='artificial-intelligence').first()
        if not ai_tag:
            ai_tag = Tag.objects.create(name='Artificial Intelligence', slug='artificial-intelligence')
        
        startup_tag = Tag.objects.filter(slug='startup').first()
        if not startup_tag:
            startup_tag = Tag.objects.create(name='Startup', slug='startup')
        
        # Create sample articles
        articles_data = [
            {
                'title': 'Getting Started with Django',
                'slug': 'getting-started-with-django',
                'excerpt': 'Learn Django basics and build your first web application.',
                'content': '''Django is a powerful web framework that makes it easy to build web applications. 

In this comprehensive guide, we'll explore:
- Django basics and architecture
- Setting up your first project
- Creating models and views
- Working with templates
- Building REST APIs

Let's dive into the world of Django development!''',
                'author': admin_user,
                'category': tech_cat,
                'tags': [python_tag],
                'reading_time': 5
            },
            {
                'title': 'Machine Learning Basics',
                'slug': 'machine-learning-basics',
                'excerpt': 'An introduction to machine learning concepts and applications.',
                'content': '''Machine learning is revolutionizing the way we interact with technology. 

This article covers:
- Supervised learning fundamentals
- Unsupervised learning techniques
- Popular ML frameworks
- Real-world applications

Learn how ML is transforming industries!''',
                'author': writer_user,
                'category': science_cat,
                'tags': [ai_tag],
                'reading_time': 8
            },
            {
                'title': 'Building a Successful Startup',
                'slug': 'building-successful-startup',
                'excerpt': 'Key strategies for launching and growing a successful startup.',
                'content': '''Starting a successful startup requires more than just a great idea. 

This comprehensive guide covers:
- Market research and validation
- Building a minimum viable product
- Funding strategies
- Team building
- Growth hacking techniques

Learn from successful entrepreneurs and avoid common pitfalls.''',
                'author': admin_user,
                'category': business_cat,
                'tags': [startup_tag],
                'reading_time': 6
            }
        ]
        
        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                slug=article_data['slug'],
                defaults={
                    'title': article_data['title'],
                    'excerpt': article_data['excerpt'],
                    'content': article_data['content'],
                    'author': article_data['author'],
                    'category': article_data['category'],
                    'reading_time': article_data['reading_time'],
                    'status': 'published'
                }
            )
            
            if created:
                article.tags.set(article_data['tags'])
                self.stdout.write(self.style.SUCCESS(f'Created article: {article.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Article already exists: {article.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'Total articles: {Article.objects.count()}'))
        
        # List all available articles
        self.stdout.write('\nAvailable articles:')
        for article in Article.objects.all():
            self.stdout.write(f'- {article.title} (slug: {article.slug})')
