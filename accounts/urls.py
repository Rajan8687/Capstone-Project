from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
