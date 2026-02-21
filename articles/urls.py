from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('articles/', views.ArticleListView.as_view(), name='article-list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('create/', views.ArticleCreateView.as_view(), name='article-create'),
    path('edit/<slug:slug>/', views.ArticleUpdateView.as_view(), name='article-edit'),
    path('delete/<slug:slug>/', views.ArticleDeleteView.as_view(), name='article-delete'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('like/<slug:slug>/', views.LikeArticleView.as_view(), name='like-article'),
    path('comment/<slug:slug>/', views.AddCommentView.as_view(), name='add-comment'),
    path('edit-comment/<int:comment_id>/', views.EditCommentView.as_view(), name='edit-comment'),
    path('delete-comment/<int:comment_id>/', views.DeleteCommentView.as_view(), name='delete-comment'),
    path('my-articles/', views.UserArticlesView.as_view(), name='user-articles'),
    path('author-article/<slug:slug>/', views.AuthorArticleDetailView.as_view(), name='author-article-detail'),
]
