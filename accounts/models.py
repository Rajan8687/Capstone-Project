from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    linkedin = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_writer(self):
        return self.role == 'writer'

    @property
    def is_admin_user(self):
        return self.role == 'admin'


class ReaderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_categories = models.JSONField(default=list, blank=True)
    reading_preferences = models.JSONField(default=dict, blank=True)
    total_articles_read = models.PositiveIntegerField(default=0)
    total_reading_time = models.PositiveIntegerField(default=0)  # in minutes
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Reader Profile"


class WriterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expertise_areas = models.JSONField(default=list, blank=True)
    total_articles_published = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_likes = models.PositiveIntegerField(default=0)
    writer_score = models.FloatField(default=0.0)  # Calculated based on engagement
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Writer Profile"

    def calculate_writer_score(self):
        """Calculate writer score based on engagement metrics"""
        if self.total_articles_published == 0:
            return 0.0
        
        avg_views_per_article = self.total_views / self.total_articles_published
        avg_likes_per_article = self.total_likes / self.total_articles_published
        
        # Weighted score: 60% views, 30% likes, 10% article count
        score = (avg_views_per_article * 0.6) + (avg_likes_per_article * 10 * 0.3) + (self.total_articles_published * 0.1)
        
        self.writer_score = round(score, 2)
        self.save()
        return self.writer_score
