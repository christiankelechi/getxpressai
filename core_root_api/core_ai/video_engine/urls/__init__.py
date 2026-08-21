"""
XPRESSAI Video Engine URLs
URL patterns for video generation API endpoints
"""

# Import available URL patterns
from .video_urls import urlpatterns as video_urlpatterns

# Import other URL patterns if they exist (will be implemented later)
try:
    from .voice_urls import urlpatterns as voice_urlpatterns
except ImportError:
    voice_urlpatterns = []

try:
    from .translation_urls import urlpatterns as translation_urlpatterns
except ImportError:
    translation_urlpatterns = []

try:
    from .analytics_urls import urlpatterns as analytics_urlpatterns
except ImportError:
    analytics_urlpatterns = []

# Combine all URL patterns
urlpatterns = []
urlpatterns.extend(video_urlpatterns)
urlpatterns.extend(voice_urlpatterns)
urlpatterns.extend(translation_urlpatterns)
urlpatterns.extend(analytics_urlpatterns)
