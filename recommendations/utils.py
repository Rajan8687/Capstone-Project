from django.utils import timezone
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import numpy as np

from articles.models import Article, Category, Tag
from analytics.models import UserBehavior, ReadingPattern
from .models import UserRecommendation, ArticleSimilarity, UserVector, ArticleVector

# Download NLTK data if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class RecommendationEngine:
    """Main recommendation engine using multiple algorithms"""
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess_text(self, text):
        """Preprocess text for TF-IDF"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def get_personalized_recommendations(self, user, limit=10):
        """Get personalized recommendations for a user"""
        recommendations = []
        
        # Get user's reading history
        user_behavior = UserBehavior.objects.filter(user=user).select_related('article')
        read_articles = [behavior.article for behavior in user_behavior]
        
        # Get user's preferred categories
        reading_patterns = ReadingPattern.objects.filter(user=user).select_related('category')
        preferred_categories = [pattern.category for pattern in reading_patterns if pattern.total_articles_read > 0]
        
        # Content-based recommendations
        content_based = self.get_content_based_recommendations(user, read_articles, preferred_categories, limit//2)
        
        # Collaborative filtering recommendations
        collaborative = self.get_collaborative_recommendations(user, read_articles, limit//2)
        
        # Combine and rank recommendations
        all_recommendations = content_based + collaborative
        
        # Remove duplicates and already read articles
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec.id not in seen and rec not in read_articles:
                seen.add(rec.id)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:limit]
    
    def get_content_based_recommendations(self, user, read_articles, preferred_categories, limit=10):
        """Get content-based recommendations"""
        if not read_articles:
            # If no reading history, recommend from preferred categories
            if preferred_categories:
                return Article.objects.filter(
                    category__in=preferred_categories,
                    status='published'
                ).exclude(id__in=[article.id for article in read_articles]).order_by('-views_count')[:limit]
            else:
                # Return popular articles
                return Article.objects.filter(
                    status='published'
                ).order_by('-views_count')[:limit]
        
        # Get TF-IDF vectors for all articles
        all_articles = Article.objects.filter(status='published')
        article_texts = [self.preprocess_text(article.content + ' ' + article.title) for article in all_articles]
        
        if not article_texts:
            return []
        
        # Fit TF-IDF vectorizer
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(article_texts)
        
        # Get user's reading history vectors
        read_indices = [all_articles.index(article) for article in read_articles if article in all_articles]
        
        if not read_indices:
            return []
        
        user_profile = tfidf_matrix[read_indices].mean(axis=0)
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(user_profile, tfidf_matrix).flatten()
        
        # Get top recommendations
        top_indices = similarity_scores.argsort()[::-1]
        
        recommendations = []
        for idx in top_indices:
            if idx < len(all_articles):
                article = all_articles[idx]
                if article not in read_articles:
                    recommendations.append(article)
                    if len(recommendations) >= limit:
                        break
        
        return recommendations
    
    def get_collaborative_recommendations(self, user, read_articles, limit=10):
        """Get collaborative filtering recommendations"""
        # Find users with similar reading patterns
        similar_users = self.find_similar_users(user, read_articles)
        
        if not similar_users:
            return []
        
        # Get articles read by similar users but not by current user
        similar_user_articles = UserBehavior.objects.filter(
            user__in=similar_users,
            action_type='view'
        ).exclude(article__in=read_articles).values_list('article', flat=True).distinct()
        
        recommendations = Article.objects.filter(
            id__in=similar_user_articles,
            status='published'
        ).annotate(
            view_count=Count('userbehavior', filter=Q(userbehavior__action_type='view'))
        ).order_by('-view_count')[:limit]
        
        return list(recommendations)
    
    def find_similar_users(self, user, read_articles, limit=10):
        """Find users with similar reading patterns"""
        read_article_ids = [article.id for article in read_articles]
        
        # Find users who have read the same articles
        similar_users = UserBehavior.objects.filter(
            article__id__in=read_article_ids,
            action_type='view'
        ).exclude(user=user).values('user').annotate(
            common_articles=Count('article', distinct=True)
        ).filter(common_articles__gte=2).order_by('-common_articles')[:limit]
        
        user_ids = [similar['user'] for similar in similar_users]
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        return User.objects.filter(id__in=user_ids)
    
    def get_trending_recommendations(self, limit=10):
        """Get trending articles"""
        return Article.objects.filter(
            status='published',
            is_trending=True
        ).select_related('author', 'category').prefetch_related('tags').order_by('-views_count')[:limit]
    
    def get_similar_articles(self, article, limit=5):
        """Get articles similar to the given article"""
        # Check if similarity is already calculated
        similarities = ArticleSimilarity.objects.filter(
            article1=article,
            similarity_type='content'
        ).select_related('article2').order_by('-similarity_score')[:limit]
        
        if similarities.exists():
            return [sim.article2 for sim in similarities]
        
        # Calculate similarity on the fly
        all_articles = Article.objects.filter(status='published').exclude(id=article.id)
        article_texts = [self.preprocess_text(a.content + ' ' + a.title) for a in all_articles]
        
        if not article_texts:
            return []
        
        # Add current article to the list
        current_text = self.preprocess_text(article.content + ' ' + article.title)
        all_texts = [current_text] + article_texts
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
        
        # Calculate similarity with current article (first row)
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Get top similar articles
        top_indices = similarity_scores.argsort()[::-1][:limit]
        
        similar_articles = []
        for idx in top_indices:
            if idx < len(all_articles):
                similar_articles.append(all_articles[idx])
        
        return similar_articles
    
    def update_article_vectors(self, article):
        """Update article feature vectors"""
        # TF-IDF vector
        text = self.preprocess_text(article.content + ' ' + article.title)
        tfidf_vector = self.tfidf_vectorizer.fit_transform([text]).toarray()[0]
        
        # Category vector (one-hot encoding)
        categories = Category.objects.all()
        category_vector = {cat.name: 1 if cat.id == article.category.id else 0 for cat in categories}
        
        # Tag vector
        tags = article.tags.all()
        tag_vector = {tag.name: 1 for tag in tags}
        
        # Article features
        length_score = len(article.content.split()) / 1000  # Normalize by 1000 words
        complexity_score = self.calculate_complexity(article.content)
        engagement_score = article.get_engagement_score()
        
        # Save vectors
        article_vector, created = ArticleVector.objects.get_or_create(article=article)
        article_vector.tfidf_vector = tfidf_vector.tolist()
        article_vector.category_vector = category_vector
        article_vector.tag_vector = tag_vector
        article_vector.length_score = length_score
        article_vector.complexity_score = complexity_score
        article_vector.engagement_score = engagement_score
        article_vector.save()
    
    def calculate_complexity(self, text):
        """Calculate text complexity score"""
        words = text.split()
        sentences = text.split('.')
        
        if not sentences:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Simple complexity score based on average sentence length
        if avg_words_per_sentence < 10:
            return 0.3  # Simple
        elif avg_words_per_sentence < 20:
            return 0.6  # Medium
        else:
            return 0.9  # Complex
    
    def update_user_vectors(self, user):
        """Update user preference vectors"""
        # Get user's reading history
        user_behavior = UserBehavior.objects.filter(user=user).select_related('article')
        
        if not user_behavior.exists():
            return
        
        # Calculate category preferences
        category_preferences = {}
        for behavior in user_behavior:
            category = behavior.article.category.name
            if category not in category_preferences:
                category_preferences[category] = 0
            category_preferences[category] += 1
        
        # Normalize preferences
        total = sum(category_preferences.values())
        if total > 0:
            category_preferences = {k: v/total for k, v in category_preferences.items()}
        
        # Calculate tag preferences
        tag_preferences = {}
        for behavior in user_behavior:
            for tag in behavior.article.tags.all():
                if tag.name not in tag_preferences:
                    tag_preferences[tag.name] = 0
                tag_preferences[tag.name] += 1
        
        # Normalize tag preferences
        total_tags = sum(tag_preferences.values())
        if total_tags > 0:
            tag_preferences = {k: v/total_tags for k, v in tag_preferences.items()}
        
        # Calculate reading preferences
        reading_sessions = ReadingPattern.objects.filter(user=user)
        avg_time = reading_sessions.aggregate(avg_time=Avg('total_time_spent'))['avg_time'] or 0
        
        # Save user vectors
        user_vector, created = UserVector.objects.get_or_create(user=user)
        user_vector.category_vector = category_preferences
        user_vector.tag_vector = tag_preferences
        user_vector.reading_time_preference = avg_time
        user_vector.save()
