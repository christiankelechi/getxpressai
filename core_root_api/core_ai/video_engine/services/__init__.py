"""
XPRESSAI Video Engine Services
AI processing services for video generation and analysis
"""

# Import available services
from .video_generation_service import VideoGenerationService

# Import other services if they exist (will be implemented later)
try:
    from .emotion_detection_service import EmotionDetectionService
except ImportError:
    EmotionDetectionService = None

try:
    from .voice_training_service import VoiceTrainingService
except ImportError:
    VoiceTrainingService = None

try:
    from .translation_service import TranslationService
except ImportError:
    TranslationService = None

__all__ = [
    'VideoGenerationService',
    'EmotionDetectionService',
    'VoiceTrainingService',
    'TranslationService',
]
