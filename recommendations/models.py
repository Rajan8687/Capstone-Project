from django.db import models
from django.contrib.auth import get_user_model
from articles.models import Article, Category

User = get_user_model()


class UserRecommendation(models.Model):
    """Store personalized recommendations for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)  # Recommendation score (0-1)
    recommendation_type = models.CharField(max_length=20, choices=[
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('trending', 'Trending'),
        ('similar_users', 'Similar Users'),
        ('category_based', 'Category-Based'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'article']
        ordering = ['-score']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.article.title} ({self.score:.2f})"


class ArticleSimilarity(models.Model):
    """Store similarity scores between articles"""
    article1 = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='similarities_1')
    article2 = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='similarities_2')
    similarity_score = models.FloatField(default=0.0)  # 0-1 similarity score
    similarity_type = models.CharField(max_length=20, choices=[
        ('content', 'Content-Based'),
        ('tags', 'Tags-Based'),
        ('category', 'Category-Based'),
        ('user_behavior', 'User Behavior'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['article1', 'article2', 'similarity_type']
        ordering = ['-similarity_score']

    def __str__(self):
        return f"Similarity: {self.article1.title} <-> {self.article2.title} ({self.similarity_score:.2f})"


class UserVector(models.Model):
    """Store user preference vectors for ML recommendations"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category_vector = models.JSONField(default=dict)  # Category preferences
    tag_vector = models.JSONField(default=dict)  # Tag preferences
    reading_time_preference = models.FloatField(default=0.0)  # Preferred reading time
    complexity_preference = models.FloatField(default=0.0)  # Content complexity preference
    update_frequency = models.IntegerField(default=24)  # Hours between updates
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preference vector for {self.user.username}"


class ArticleVector(models.Model):
    """Store article feature vectors for ML recommendations"""
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    tfidf_vector = models.JSONField(default=dict)  # TF-IDF vector
    category_vector = models.JSONField(default=dict)  # Category encoding
    tag_vector = models.JSONField(default=dict)  # Tag encoding
    length_score = models.FloatField(default=0.0)  # Article length preference
    complexity_score = models.FloatField(default=0.0)  # Content complexity
    engagement_score = models.FloatField(default=0.0)  # Historical engagement
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feature vector for {self.article.title}"


class RecommendationFeedback(models.Model):
    """Track user feedback on recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    recommendation = models.ForeignKey(UserRecommendation, on_delete=models.CASCADE, null=True, blank=True)
    feedback_type = models.CharField(max_length=20, choices=[
        ('clicked', 'Clicked'),
        ('liked', 'Liked'),
        ('bookmarked', 'Bookmarked'),
        ('shared', 'Shared'),
        ('not_interested', 'Not Interested'),
        ('hide', 'Hide Recommendation'),
    ])
    feedback_value = models.FloatField(default=0.0)  # Positive or negative feedback score
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'feedback_type']),
            models.Index(fields=['article', 'feedback_type']),
        ]

    def __str__(self):
        return f"{self.user.username} feedback: {self.feedback_type} for {self.article.title}"


class TrendingPrediction(models.Model):
    """Store ML predictions for trending articles"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    prediction_date = models.DateTimeField()
    predicted_score = models.FloatField(default=0.0)
    prediction_confidence = models.FloatField(default=0.0)  # 0-1 confidence
    actual_score = models.FloatField(null=True, blank=True)  # Actual score when known
    model_version = models.CharField(max_length=20, default='v1.0')
    features_used = models.JSONField(default=list)  # List of features used in prediction
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prediction_date']
        indexes = [
            models.Index(fields=['article', '-prediction_date']),
            models.Index(fields=['-predicted_score']),
        ]

    def __str__(self):
        return f"Prediction for {self.article.title}: {self.predicted_score:.2f} (confidence: {self.prediction_confidence:.2f})"

    def calculate_accuracy(self):
        """Calculate prediction accuracy when actual score is known"""
        if self.actual_score is not None:
            accuracy = 1 - abs(self.predicted_score - self.actual_score) / max(self.actual_score, self.predicted_score)
            return max(0, accuracy)  # Ensure non-negative
        return None
