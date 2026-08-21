"""
XPRESSAI Video Engine Views
REST API endpoints for video generation operations
"""

# Import only existing views
from .video_views import *

# Other views will be implemented when needed
# from .voice_views import *
# from .translation_views import *
# from .analytics_views import *

__all__ = [
    # Video views (implemented)
    'VideoGenerationProjectViewSet',
    'VideoSegmentViewSet',
    'VideoTemplateViewSet',
    'VideoProcessingQueueViewSet',

    # Voice views (to be implemented)
    # 'VoiceProfileViewSet',
    # 'VoiceTrainingSessionViewSet',

    # Translation views (to be implemented)
    # 'TranslationRequestViewSet',
    # 'TranslationMemoryViewSet',

    # Analytics views (to be implemented)
    # 'VideoAnalyticsViewSet',
    # 'EmotionDetectionResultViewSet',
]
