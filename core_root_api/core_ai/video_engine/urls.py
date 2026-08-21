"""
XPRESSAI Video Engine URLs
Main URL configuration for the video engine API
"""

from django.urls import path, include

app_name = 'video_engine'

urlpatterns = [
    # Include video generation URLs
    path('', include('core_root_api.core_ai.video_engine.urls.video_urls')),
]
