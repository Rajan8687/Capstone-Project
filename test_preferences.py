#!/usr/bin/env python3

import os
import sys

# Add project path
sys.path.append('/home/kali/Desktop/capstone-project')

# Test basic imports
try:
    print("🔍 Testing basic imports...")
    
    # Test Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insightwrite.settings')
    
    # Test our config function
    from insightwrite.settings import config
    print("✅ Config function imported successfully")
    
    # Test config function
    secret_key = config('SECRET_KEY', default='test-key')
    debug = config('DEBUG', default=True, cast=bool)
    print(f"✅ Config function works: SECRET_KEY={secret_key[:10]}..., DEBUG={debug}")
    
    # Test Django import
    import django
    django.setup()
    print("✅ Django setup successful")
    
    # Test models
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print(f"✅ User model imported: {User.__name__}")
    
    # Test article model
    from articles.models import Article, Category
    print(f"✅ Article models imported")
    
    # Test recommendation models
    from recommendations.models import UserRecommendation
    print(f"✅ Recommendation models imported")
    
    # Check data
    user_count = User.objects.count()
    article_count = Article.objects.count()
    category_count = Category.objects.count()
    
    print(f"\n📊 Database stats:")
    print(f"   Users: {user_count}")
    print(f"   Articles: {article_count}")
    print(f"   Categories: {category_count}")
    
    print("\n🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
