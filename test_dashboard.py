#!/usr/bin/env python3

import os
import sys

# Add project path
sys.path.append('/home/kali/Desktop/capstone-project')

# Test dashboard functionality
try:
    print("🧪 Testing Dashboard Functionality...")
    
    # Test Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
    
    # Test Django import
    import django
    django.setup()
    print("✅ Django setup successful")
    
    # Test models
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("✅ User model imported")
    
    from articles.models import Article
    print("✅ Article model imported")
    
    from accounts.models import ReaderProfile, WriterProfile
    print("✅ Profile models imported")
    
    # Check if users exist
    user_count = User.objects.count()
    print(f"📊 Total users: {user_count}")
    
    # Check if articles exist
    article_count = Article.objects.count()
    print(f"📄 Total articles: {article_count}")
    
    # Check profiles
    reader_profiles = ReaderProfile.objects.count()
    writer_profiles = WriterProfile.objects.count()
    print(f"👥 Reader profiles: {reader_profiles}")
    print(f"✍️  Writer profiles: {writer_profiles}")
    
    # Test dashboard view
    from accounts.views import DashboardView
    print("✅ DashboardView imported")
    
    # Test URL patterns
    from django.urls import reverse
    try:
        dashboard_url = reverse('dashboard')
        print(f"✅ Dashboard URL: {dashboard_url}")
    except Exception as e:
        print(f"❌ Dashboard URL error: {e}")
    
    try:
        user_articles_url = reverse('user-articles')
        print(f"✅ User articles URL: {user_articles_url}")
    except Exception as e:
        print(f"❌ User articles URL error: {e}")
    
    print("\n🎉 Dashboard test completed!")
    print("\n📝 Manual Testing Steps:")
    print("1. Open browser → http://localhost:8000")
    print("2. Login with admin/admin123 or writer/writer123")
    print("3. Visit: http://localhost:8000/accounts/dashboard/")
    print("4. Check if dashboard loads properly")
    print("5. Verify stats are displayed correctly")
    print("6. Test navigation links")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
