from rest_framework import serializers
from .models import Article, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'color', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'tags', 'content',
            'excerpt', 'featured_image', 'status', 'views_count', 'likes_count',
            'comments_count', 'reading_time', 'is_featured', 'is_trending',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['views_count', 'likes_count', 'comments_count', 'reading_time']
