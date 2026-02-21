from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from analytics.models import UserBehavior, UserJourney
import json


class AnalyticsMiddleware:
    """Middleware to track user behavior and analytics"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only track authenticated users
        if not isinstance(request.user, AnonymousUser):
            self.track_user_journey(request)
        
        return response
    
    def track_user_journey(self, request):
        """Track user journey through the site"""
        # Get session ID
        session_id = request.session.session_key or 'anonymous'
        
        # Get current page
        page_visited = request.get_full_path()
        
        # Skip certain pages
        skip_paths = ['/static/', '/media/', '/favicon.ico']
        if any(page_visited.startswith(path) for path in skip_paths):
            return
        
        # Create or update user journey
        journey = UserJourney.objects.create(
            user=request.user,
            session_id=session_id,
            page_visited=page_visited,
            entry_point=request.META.get('HTTP_REFERER', '')
        )
        
        # Store journey ID in session for tracking
        request.session['current_journey_id'] = journey.id
