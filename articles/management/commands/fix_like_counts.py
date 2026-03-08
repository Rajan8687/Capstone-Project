from django.core.management.base import BaseCommand
from articles.models import Article, Like


class Command(BaseCommand):
    help = 'Fix like counts for all articles'

    def handle(self, *args, **options):
        self.stdout.write('Fixing like counts for all articles...')
        
        fixed_count = 0
        for article in Article.objects.all():
            actual_likes = Like.objects.filter(article=article).count()
            
            if article.likes_count != actual_likes:
                self.stdout.write(f'Fixing "{article.title}": {article.likes_count} -> {actual_likes}')
                article.likes_count = actual_likes
                article.save()
                fixed_count += 1
            else:
                self.stdout.write(f'OK "{article.title}": {actual_likes} likes')
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} articles!'))
