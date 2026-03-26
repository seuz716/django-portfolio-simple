"""
Rate Limiting Configuration
Protect against brute force and DoS attacks
"""

# Add to views that need rate limiting:
# @ratelimit(key='ip', rate='5/m', block=True)

# Example usage in views.py:
"""
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def login_view(request):
    # Login logic here
    pass

@ratelimit(key='user_or_ip', rate='5/m', block=True)
def contact_form(request):
    # Contact form logic
    pass

@ratelimit(key='ip', rate='100/h', block=False)
def api_endpoint(request):
    # API endpoint with soft limiting
    was_limited = getattr(request, 'was_limited', False)
    if was_limited:
        # Return error or degraded service
        pass
"""

# Recommended rates:
# - Login attempts: 5 per minute per IP
# - Password reset: 3 per hour per IP
# - Contact forms: 10 per hour per IP
# - API endpoints: 100 per hour per IP
# - Search: 30 per minute per IP

# Install django-ratelimit:
# pip install django-ratelimit

# Add to INSTALLED_APPS:
# 'django_ratelimit',

# Add to MIDDLEWARE (after CommonMiddleware):
# 'django_ratelimit.middleware.RatelimitMiddleware',
