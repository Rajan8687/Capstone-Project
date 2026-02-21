from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Article, Category, Tag
from .serializers import ArticleSerializer, CategorySerializer, TagSerializer
from recommendations.utils import RecommendationEngine


class ArticleListAPIView(generics.ListAPIView):
    queryset = Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]


class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def RecommendationAPIView(request):
    """Get personalized recommendations for the authenticated user"""
    engine = RecommendationEngine()
    recommendations = engine.get_personalized_recommendations(request.user, limit=10)
    
    serializer = ArticleSerializer(recommendations, many=True)
    return Response({
        'recommendations': serializer.data
    })
