"""
XPRESSAI Video Engine - Analytics Models
Database models for video analytics and emotion detection
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class VideoAnalytics(models.Model):
    """
    Model for storing video performance and user interaction analytics
    """

    analytics_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Related video project
    video_project = models.ForeignKey(
        'video_engine.VideoGenerationProject',
        on_delete=models.CASCADE,
        related_name='analytics'
    )

    # View metrics
    view_count = models.PositiveIntegerField(default=0)
    unique_viewers = models.PositiveIntegerField(default=0)

    # Engagement metrics
    watch_time = models.DurationField(blank=True, null=True)
    completion_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True
    )

    # Interaction data
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    bookmarks = models.PositiveIntegerField(default=0)

    # Performance metrics
    load_time = models.FloatField(
        blank=True,
        null=True,
        help_text="Average load time in seconds"
    )
    buffering_events = models.PositiveIntegerField(default=0)
    buffering_duration = models.DurationField(blank=True, null=True)

    # Geographic data
    viewer_locations = models.JSONField(
        default=dict,
        blank=True,
        help_text="Geographic distribution of viewers"
    )

    # Device and platform data
    device_types = models.JSONField(
        default=dict,
        blank=True,
        help_text="Device type distribution"
    )
    platforms = models.JSONField(
        default=dict,
        blank=True,
        help_text="Platform distribution"
    )

    # Time-based data
    hourly_views = models.JSONField(
        default=dict,
        blank=True,
        help_text="Views by hour of day"
    )
    daily_views = models.JSONField(
        default=dict,
        blank=True,
        help_text="Views by day"
    )

    # Quality metrics
    average_quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video_project']),
            models.Index(fields=['created_at']),
            models.Index(fields=['view_count']),
        ]

    def __str__(self):
        return f"Analytics for {self.video_project.title}"

    def get_total_engagement(self):
        """
        Calculate total engagement score
        """
        return self.likes + self.shares + self.comments + self.bookmarks

    def get_average_watch_time(self):
        """
        Calculate average watch time per view
        """
        if self.view_count > 0 and self.watch_time:
            return self.watch_time.total_seconds() / self.view_count
        return 0

    def update_view_metrics(self, viewer_ip=None, user_agent=None, location=None):
        """
        Update view metrics with new view data
        """
        self.view_count += 1

        # Track unique viewers (simplified - in production you'd use sessions)
        if viewer_ip:
            # Logic to track unique viewers
            pass

        # Update geographic data
        if location:
            self._update_location_data(location)

        # Update device/platform data
        if user_agent:
            self._update_device_data(user_agent)

        self.save()

    def _update_location_data(self, location):
        """
        Update geographic distribution data
        """
        if not self.viewer_locations:
            self.viewer_locations = {}

        country = location.get('country', 'Unknown')
        if country in self.viewer_locations:
            self.viewer_locations[country] += 1
        else:
            self.viewer_locations[country] = 1

    def _update_device_data(self, user_agent):
        """
        Update device and platform data
        """
        # Simplified device detection - in production use a proper library
        if 'mobile' in user_agent.lower():
            device_type = 'mobile'
        elif 'tablet' in user_agent.lower():
            device_type = 'tablet'
        else:
            device_type = 'desktop'

        if not self.device_types:
            self.device_types = {}

        if device_type in self.device_types:
            self.device_types[device_type] += 1
        else:
            self.device_types[device_type] = 1


class EmotionDetectionResult(models.Model):
    """
    Model to store emotion detection results from video analysis
    """

    result_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Related video project
    video_project = models.ForeignKey(
        'video_engine.VideoGenerationProject',
        on_delete=models.CASCADE,
        related_name='emotion_results'
    )

    # Detection metadata
    timestamp = models.FloatField(
        help_text="Timestamp in video where emotion was detected (seconds)"
    )

    # Emotion data
    emotion = models.CharField(
        max_length=50,
        help_text="Detected emotion (happy, sad, angry, etc.)"
    )

    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score of emotion detection (0.0 to 1.0)"
    )

    # Facial data
    facial_landmarks = models.JSONField(
        blank=True,
        null=True,
        help_text="Facial landmark coordinates"
    )

    # Face detection info
    face_bounding_box = models.JSONField(
        blank=True,
        null=True,
        help_text="Face bounding box coordinates [x, y, width, height]"
    )

    # Additional metadata
    intensity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="Intensity of the detected emotion (0.0 to 1.0)"
    )

    # Processing info
    detection_method = models.CharField(
        max_length=50,
        default='mediapipe',
        help_text="Method used for emotion detection"
    )

    frame_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Frame number in the video"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['video_project', 'timestamp']),
            models.Index(fields=['emotion']),
            models.Index(fields=['confidence']),
        ]

    def __str__(self):
        return f"{self.emotion} at {self.timestamp}s - {self.video_project.title}"

    def get_emotion_category(self):
        """
        Get emotion category for grouping
        """
        emotion_categories = {
            'positive': ['happy', 'joy', 'excited', 'surprised'],
            'negative': ['sad', 'angry', 'fear', 'disgust'],
            'neutral': ['neutral', 'confused', 'bored']
        }

        for category, emotions in emotion_categories.items():
            if self.emotion.lower() in emotions:
                return category
        return 'unknown'


class UserInteractionLog(models.Model):
    """
    Model for logging detailed user interactions with videos
    """

    log_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Related models
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_interactions'
    )

    video_project = models.ForeignKey(
        'video_engine.VideoGenerationProject',
        on_delete=models.CASCADE,
        related_name='interaction_logs'
    )

    # Interaction details
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('comment', 'Comment'),
        ('bookmark', 'Bookmark'),
        ('pause', 'Pause'),
        ('seek', 'Seek'),
        ('complete', 'Complete'),
    ]

    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES
    )

    # Timing information
    timestamp = models.DateTimeField(auto_now_add=True)
    video_timestamp = models.FloatField(
        blank=True,
        null=True,
        help_text="Timestamp in video where interaction occurred"
    )

    # Context data
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    location = models.JSONField(blank=True, null=True)

    # Additional data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional interaction metadata"
    )

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['video_project', 'interaction_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} on {self.video_project.title}"


class PerformanceMetrics(models.Model):
    """
    Model for storing system performance metrics
    """

    metrics_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Metric type
    METRIC_TYPES = [
        ('cpu_usage', 'CPU Usage'),
        ('memory_usage', 'Memory Usage'),
        ('gpu_usage', 'GPU Usage'),
        ('disk_usage', 'Disk Usage'),
        ('network_io', 'Network I/O'),
        ('processing_time', 'Processing Time'),
        ('api_response_time', 'API Response Time'),
    ]

    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES
    )

    # Metric value
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='percent')

    # Context
    component = models.CharField(
        max_length=100,
        help_text="Component or service being measured"
    )

    # Thresholds
    warning_threshold = models.FloatField(blank=True, null=True)
    critical_threshold = models.FloatField(blank=True, null=True)

    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)
    server_node = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_type', 'recorded_at']),
            models.Index(fields=['component']),
        ]

    def __str__(self):
        return f"{self.metric_type}: {self.value}{self.unit}"

    def is_warning(self):
        """
        Check if metric is in warning range
        """
        if self.warning_threshold:
            return self.value >= self.warning_threshold
        return False

    def is_critical(self):
        """
        Check if metric is in critical range
        """
        if self.critical_threshold:
            return self.value >= self.critical_threshold
        return False
