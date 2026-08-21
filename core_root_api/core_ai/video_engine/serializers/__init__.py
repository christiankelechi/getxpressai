"""
XPRESSAI Video Engine Serializers
Data serialization for API responses and requests
"""

# Import only existing serializers
from .video_serializers import *

# Other serializers will be implemented when needed
# from .voice_serializers import *
# from .translation_serializers import *
# from .analytics_serializers import *

__all__ = [
    # Video serializers (implemented)
    'VideoGenerationProjectSerializer',
    'VideoSegmentSerializer',
    'VideoTemplateSerializer',
    'VideoProcessingQueueSerializer',
    'VideoGenerationRequestSerializer',
    'VideoProjectUpdateSerializer',
    'BulkVideoOperationSerializer',
    'VideoAnalyticsSerializer',
    'VideoStatusResponseSerializer',

    # Voice serializers (to be implemented)
    # 'VoiceProfileSerializer',
    # 'VoiceTrainingSessionSerializer',

    # Translation serializers (to be implemented)
    # 'TranslationRequestSerializer',
    # 'TranslationMemorySerializer',

    # Analytics serializers (to be implemented)
    # 'VideoAnalyticsSerializer',
    # 'EmotionDetectionResultSerializer',
]
