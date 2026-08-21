"""
XPRESSAI Video Engine - Voice Models
Database models for voice profile management and training
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class VoiceProfile(models.Model):
    """
    Model for custom voice profiles and training data
    """

    profile_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='voice_profiles'
    )

    name = models.CharField(
        max_length=100,
        help_text="Name of the voice profile"
    )

    # Voice characteristics
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('neutral', 'Neutral'),
        ],
        default='neutral'
    )

    accent = models.CharField(
        max_length=50,
        blank=True,
        help_text="Accent type for the voice"
    )

    # Training data
    training_audio_files = models.JSONField(
        default=list,
        help_text="List of training audio file paths"
    )

    # Model paths
    voice_model_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Path to trained voice model"
    )

    # Status
    STATUS_CHOICES = [
        ('training', 'Training'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='training'
    )

    # Quality metrics
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True
    )

    # Training metadata
    training_started_at = models.DateTimeField(blank=True, null=True)
    training_completed_at = models.DateTimeField(blank=True, null=True)
    training_duration = models.DurationField(blank=True, null=True)

    # Voice specifications
    sample_rate = models.PositiveIntegerField(default=22050)
    language = models.CharField(max_length=10, default='en')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def is_training_complete(self):
        """
        Check if voice training is complete
        """
        return self.status == 'ready'

    def can_start_training(self):
        """
        Check if profile can start training
        """
        return self.status == 'training' and len(self.training_audio_files) >= 3

    def get_training_duration(self):
        """
        Get total training time
        """
        if self.training_started_at and self.training_completed_at:
            return self.training_completed_at - self.training_started_at
        return None

    def add_training_sample(self, file_path):
        """
        Add a training audio sample
        """
        if not self.training_audio_files:
            self.training_audio_files = []
        self.training_audio_files.append(file_path)
        self.save(update_fields=['training_audio_files'])

    def remove_training_sample(self, file_path):
        """
        Remove a training audio sample
        """
        if file_path in self.training_audio_files:
            self.training_audio_files.remove(file_path)
            self.save(update_fields=['training_audio_files'])


class VoiceTrainingSession(models.Model):
    """
    Model to track voice training sessions
    """

    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    voice_profile = models.ForeignKey(
        VoiceProfile,
        on_delete=models.CASCADE,
        related_name='training_sessions'
    )

    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Training configuration
    training_config = models.JSONField(
        default=dict,
        help_text="Training configuration parameters"
    )

    # Training metrics
    epochs_completed = models.PositiveIntegerField(default=0)
    total_epochs = models.PositiveIntegerField(default=100)
    current_loss = models.FloatField(blank=True, null=True)
    best_loss = models.FloatField(blank=True, null=True)

    # Status
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('stopped', 'Stopped'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='running'
    )

    # Error handling
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['voice_profile', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Training session for {self.voice_profile.name}"

    def get_progress_percentage(self):
        """
        Calculate training progress percentage
        """
        if self.total_epochs > 0:
            return (self.epochs_completed / self.total_epochs) * 100
        return 0

    def update_progress(self, epoch, loss):
        """
        Update training progress
        """
        self.epochs_completed = epoch
        self.current_loss = loss

        if self.best_loss is None or loss < self.best_loss:
            self.best_loss = loss

        self.save(update_fields=['epochs_completed', 'current_loss', 'best_loss'])


class VoiceSample(models.Model):
    """
    Model for individual voice training samples
    """

    sample_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    voice_profile = models.ForeignKey(
        VoiceProfile,
        on_delete=models.CASCADE,
        related_name='voice_samples'
    )

    # File information
    audio_file = models.FileField(upload_to='voice_samples/')
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()

    # Audio metadata
    duration = models.FloatField(help_text="Duration in seconds")
    sample_rate = models.PositiveIntegerField()
    channels = models.PositiveIntegerField(default=1)

    # Quality metrics
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True
    )

    # Processing status
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded'
    )

    # Rejection reason
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['voice_profile', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Sample: {self.file_name}"

    def get_audio_url(self):
        """
        Get the URL for the audio file
        """
        if self.audio_file:
            return self.audio_file.url
        return None

    def mark_processed(self, quality_score=None):
        """
        Mark sample as processed
        """
        self.status = 'processed'
        if quality_score is not None:
            self.quality_score = quality_score
        self.save()

    def mark_rejected(self, reason):
        """
        Mark sample as rejected
        """
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()
