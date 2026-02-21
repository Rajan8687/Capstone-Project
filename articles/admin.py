from django.contrib import admin
from .models import Article, Category, Tag, Like, Comment, ReadingSession, ArticleView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_article_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('get_article_count',)
    
    def get_article_count(self, obj):
        return obj.get_article_count()
    get_article_count.short_description = 'Published Articles'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views_count', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('status', 'category', 'created_at', 'is_featured', 'is_trending')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'likes_count', 'comments_count', 'reading_time', 'get_like_percentage', 'get_engagement_score')
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'status')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_trending')
        }),
        ('Analytics', {
            'fields': ('views_count', 'likes_count', 'comments_count', 'reading_time', 'get_like_percentage', 'get_engagement_score'),
            'classes': ('collapse',)
        }),
    )
    
    def get_like_percentage(self, obj):
        return f"{obj.get_like_percentage()}%"
    get_like_percentage.short_description = 'Like %'
    
    def get_engagement_score(self, obj):
        return f"{obj.get_engagement_score()}%"
    get_engagement_score.short_description = 'Engagement'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title')
    date_hierarchy = 'created_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'content_preview', 'sentiment_score', 'created_at')
    list_filter = ('created_at', 'sentiment_score')
    search_fields = ('user__username', 'article__title', 'content')
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'time_spent', 'scroll_percentage', 'completed', 'created_at')
    list_filter = ('completed', 'created_at')
    search_fields = ('user__username', 'article__title')
    date_hierarchy = 'created_at'


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title', 'ip_address')
    date_hierarchy = 'created_at'
    readonly_fields = ('user_agent', 'referrer')
