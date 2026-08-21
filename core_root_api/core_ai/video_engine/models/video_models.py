"""
XPRESSAI Video Engine - Video Models
Database models for video generation and processing
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import default_storage
import uuid
import os
from datetime import timedelta

User = get_user_model()


class VideoGenerationProject(models.Model):
    """
    Main project model for video generation tasks
    Handles the overall video creation workflow and metadata
    """

    # Unique identifier for the project
    project_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the video generation project"
    )

    # Relationship to the user who created the project
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='video_projects',
        help_text="User who owns this video generation project"
    )

    # Project metadata
    title = models.CharField(
        max_length=200,
        help_text="Descriptive title for the video project"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the video content"
    )

    # Project status tracking
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the video generation process"
    )

    # Video generation parameters
    prompt = models.TextField(
        help_text="The main prompt used for video generation"
    )
    duration = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(300)],
        help_text="Desired duration of the video in seconds"
    )

    # AI model configuration
    ai_model = models.CharField(
        max_length=100,
        default='stable-diffusion-video',
        help_text="AI model used for video generation"
    )
    model_version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Specific version of the AI model"
    )

    # Output configuration
    resolution = models.CharField(
        max_length=20,
        default='720p',
        choices=[
            ('480p', '480p'),
            ('720p', '720p'),
            ('1080p', '1080p'),
            ('4k', '4K'),
        ],
        help_text="Video resolution for output"
    )

    # Multilingual support
    language = models.CharField(
        max_length=10,
        default='en',
        help_text="Primary language for the video content"
    )
    target_languages = models.JSONField(
        default=list,
        blank=True,
        help_text="List of languages to generate translations for"
    )

    # Voice configuration
    voice_type = models.CharField(
        max_length=50,
        default='default',
        help_text="Type of voice to use for narration"
    )
    custom_voice = models.BooleanField(
        default=False,
        help_text="Whether to use a custom trained voice"
    )

    # File storage paths
    video_file = models.FileField(
        upload_to='generated_videos/',
        blank=True,
        null=True,
        help_text="Path to the generated video file"
    )
    thumbnail = models.ImageField(
        upload_to='video_thumbnails/',
        blank=True,
        null=True,
        help_text="Thumbnail image for the video"
    )

    # Processing metadata
    processing_started_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when video processing started"
    )
    processing_completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when video processing completed"
    )
    processing_duration = models.DurationField(
        blank=True,
        null=True,
        help_text="Total time taken for video processing"
    )

    # Quality and performance metrics
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text="AI-generated quality score (0.0 to 1.0)"
    )
    file_size = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        help_text="Size of the generated video file in bytes"
    )

    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text="Error message if video generation failed"
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times processing has been retried"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['ai_model']),
        ]
        verbose_name = "Video Generation Project"
        verbose_name_plural = "Video Generation Projects"

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def get_video_url(self):
        """
        Get the full URL for the generated video file
        """
        if self.video_file:
            return self.video_file.url
        return None

    def get_processing_time(self):
        """
        Calculate the processing time if available
        """
        if self.processing_started_at and self.processing_completed_at:
            return self.processing_completed_at - self.processing_started_at
        return None

    def is_processing_complete(self):
        """
        Check if video processing is complete
        """
        return self.status == 'completed'

    def can_start_processing(self):
        """
        Check if project can start processing
        """
        return self.status == 'draft' and self.retry_count < 3


class VideoSegment(models.Model):
    """
    Model for individual segments within a video project
    Allows for modular video composition and editing
    """

    segment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Relationship to parent project
    project = models.ForeignKey(
        VideoGenerationProject,
        on_delete=models.CASCADE,
        related_name='segments'
    )

    # Segment metadata
    title = models.CharField(
        max_length=100,
        help_text="Title of this video segment"
    )
    order = models.PositiveIntegerField(
        help_text="Order of this segment in the video"
    )

    # Content configuration
    prompt = models.TextField(
        help_text="Specific prompt for this segment"
    )
    duration = models.PositiveIntegerField(
        help_text="Duration of this segment in seconds"
    )

    # AI processing
    ai_model = models.CharField(
        max_length=100,
        help_text="AI model used for this segment"
    )

    # File paths
    video_file = models.FileField(
        upload_to='video_segments/',
        blank=True,
        null=True
    )
    audio_file = models.FileField(
        upload_to='segment_audio/',
        blank=True,
        null=True
    )

    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ['project', 'order']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Segment {self.order}: {self.title}"

    def get_segment_url(self):
        """
        Get the URL for this segment's video file
        """
        if self.video_file:
            return self.video_file.url
        return None


class VideoTemplate(models.Model):
    """
    Model for reusable video templates
    """

    template_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Template configuration
    template_config = models.JSONField(
        help_text="JSON configuration for the template"
    )

    # Template metadata
    category = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list, blank=True)

    # Usage statistics
    usage_count = models.PositiveIntegerField(default=0)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        blank=True,
        null=True
    )

    # Template author
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_templates'
    )

    # Visibility
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_count', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.name

    def increment_usage(self):
        """
        Increment usage count when template is used
        """
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class VideoProcessingQueue(models.Model):
    """
    Model for managing video processing queue
    """

    queue_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    project = models.ForeignKey(
        VideoGenerationProject,
        on_delete=models.CASCADE,
        related_name='queue_entries'
    )

    # Queue management
    priority = models.PositiveIntegerField(default=1)
    position = models.PositiveIntegerField(blank=True, null=True)

    # Processing details
    processing_node = models.CharField(max_length=100, blank=True)
    gpu_required = models.BooleanField(default=False)

    # Queue status
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )

    # Timing
    queued_at = models.DateTimeField(auto_now_add=True)
    processing_started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['priority', 'queued_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"Queue entry for {self.project.title}"

    def get_queue_wait_time(self):
        """
        Calculate how long this item has been in queue
        """
        from django.utils import timezone
        if self.processing_started_at:
            return self.processing_started_at - self.queued_at
        return timezone.now() - self.queued_at
