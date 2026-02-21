from django.db import models
from django.contrib.auth import get_user_model
from articles.models import Article, Category

User = get_user_model()


class UserBehavior(models.Model):
    """Track detailed user behavior for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=[
        ('view', 'View'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('share', 'Share'),
        ('bookmark', 'Bookmark'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    time_on_page = models.PositiveIntegerField(default=0)  # in seconds
    scroll_depth = models.FloatField(default=0.0)  # 0 to 1

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['article', 'action_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} {self.action_type} {self.article.title}"


class ReadingPattern(models.Model):
    """Analyze reading patterns and preferences"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_articles_read = models.PositiveIntegerField(default=0)
    total_time_spent = models.PositiveIntegerField(default=0)  # in minutes
    average_reading_speed = models.FloatField(default=0.0)  # words per minute
    completion_rate = models.FloatField(default=0.0)  # percentage of articles completed
    preferred_reading_time = models.CharField(max_length=20, choices=[
        ('morning', 'Morning (6AM-12PM)'),
        ('afternoon', 'Afternoon (12PM-6PM)'),
        ('evening', 'Evening (6PM-12AM)'),
        ('night', 'Night (12AM-6AM)'),
    ], blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category']

    def __str__(self):
        return f"{self.user.username}'s reading pattern for {self.category.name}"


class TrendingScore(models.Model):
    """Calculate and store trending scores for articles"""
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    views_velocity = models.FloatField(default=0.0)  # Views per hour
    likes_velocity = models.FloatField(default=0.0)  # Likes per hour
    comments_velocity = models.FloatField(default=0.0)  # Comments per hour
    engagement_rate = models.FloatField(default=0.0)  # (likes + comments) / views
    prediction_score = models.FloatField(default=0.0)  # ML prediction score
    last_calculated = models.DateTimeField(auto_now=True)
    trend_period = models.IntegerField(default=24)  # Hours to consider for trending

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"Trending score for {self.article.title}: {self.score}"

    def calculate_trending_score(self):
        """Calculate trending score based on recent activity"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get recent activity (last 24 hours by default)
        cutoff_time = timezone.now() - timedelta(hours=self.trend_period)
        
        recent_views = self.article.article_views.filter(created_at__gte=cutoff_time).count()
        recent_likes = self.article.likes.filter(created_at__gte=cutoff_time).count()
        recent_comments = self.article.comments.filter(created_at__gte=cutoff_time).count()
        
        # Calculate velocities (per hour)
        hours = max(1, self.trend_period)
        self.views_velocity = recent_views / hours
        self.likes_velocity = recent_likes / hours
        self.comments_velocity = recent_comments / hours
        
        # Calculate engagement rate
        total_views = max(1, self.article.views_count)
        total_engagement = self.article.likes_count + self.article.comments_count
        self.engagement_rate = total_engagement / total_views
        
        # Calculate trending score (weighted formula)
        # 40% views velocity, 30% likes velocity, 20% comments velocity, 10% engagement rate
        self.score = (
            self.views_velocity * 0.4 +
            self.likes_velocity * 10 * 0.3 +  # Multiply likes by 10 to give it more weight
            self.comments_velocity * 20 * 0.2 +  # Multiply comments by 20
            self.engagement_rate * 100 * 0.1
        )
        
        self.save()
        return self.score


class ContentPerformance(models.Model):
    """Track content performance metrics"""
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    date = models.DateField()
    daily_views = models.PositiveIntegerField(default=0)
    daily_likes = models.PositiveIntegerField(default=0)
    daily_comments = models.PositiveIntegerField(default=0)
    daily_shares = models.PositiveIntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0)  # Percentage of users who leave immediately
    avg_time_on_page = models.FloatField(default=0.0)  # in seconds
    conversion_rate = models.FloatField(default=0.0)  # Percentage of viewers who engage
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['article', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Performance for {self.article.title} on {self.date}"


class UserJourney(models.Model):
    """Track user journey through the platform"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100)
    page_visited = models.URLField()
    time_on_page = models.PositiveIntegerField(default=0)
    entry_point = models.URLField(blank=True)  # How they entered the site
    exit_point = models.BooleanField(default=False)
    conversion_actions = models.JSONField(default=list, blank=True)  # Track conversions
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        user_str = f"{self.user.username}" if self.user else "Anonymous"
        return f"{user_str} journey: {self.page_visited}"
