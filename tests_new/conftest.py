"""
Django Portfolio - Test Suite Configuration
Lead SDET: QA Architecture Implementation
"""
import os
import sys
import django
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_portfolio.settings')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only-min-50-chars-random-string')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver')

django.setup()

# Pytest configuration
pytest_plugins = [
    'tests_new.fixtures',
]

# Django pytest settings
def pytest_configure():
    from django.conf import settings
    settings.TESTING = True
