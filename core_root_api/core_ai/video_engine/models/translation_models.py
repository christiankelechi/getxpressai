"""
XPRESSAI Video Engine - Translation Models
Database models for multilingual content translation
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class TranslationRequest(models.Model):
    """
    Model for managing video translation requests
    """

    request_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Related models
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='translation_requests'
    )

    # Translation content
    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)

    original_text = models.TextField()
    translated_text = models.TextField(blank=True)

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

    # Translation service used
    translation_service = models.CharField(
        max_length=50,
        default='google_translate'
    )

    # Quality metrics
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True
    )

    # Timing
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['source_language', 'target_language']),
        ]

    def __str__(self):
        return f"{self.source_language} -> {self.target_language}"

    def get_processing_time(self):
        """
        Calculate processing time
        """
        if self.completed_at and self.requested_at:
            return self.completed_at - self.requested_at
        return None

    def can_retry(self):
        """
        Check if translation can be retried
        """
        return self.status == 'failed' and self.retry_count < 3

    def mark_completed(self, translated_text, quality_score=None):
        """
        Mark translation as completed
        """
        from django.utils import timezone

        self.status = 'completed'
        self.translated_text = translated_text
        self.completed_at = timezone.now()
        if quality_score is not None:
            self.quality_score = quality_score
        self.save()


class TranslationMemory(models.Model):
    """
    Model for storing translation memory entries
    """

    memory_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Language pair
    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)

    # Translation content
    source_text = models.TextField()
    target_text = models.TextField()

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='translation_memories'
    )

    # Usage statistics
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)

    # Quality and context
    context = models.TextField(blank=True)
    domain = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-usage_count', '-last_used']
        indexes = [
            models.Index(fields=['source_language', 'target_language']),
            models.Index(fields=['usage_count']),
        ]
        unique_together = ['source_text', 'target_text', 'source_language', 'target_language']

    def __str__(self):
        return f"TM: {self.source_language} -> {self.target_language}"

    def record_usage(self):
        """
        Record that this translation memory entry was used
        """
        from django.utils import timezone

        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])


class TranslationGlossary(models.Model):
    """
    Model for storing translation glossaries
    """

    glossary_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Ownership
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='translation_glossaries'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Language pair
    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)

    # Visibility
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name', 'source_language', 'target_language']

    def __str__(self):
        return f"Glossary: {self.name}"

    def get_entries_count(self):
        """
        Get count of glossary entries
        """
        return self.glossary_entries.count()


class GlossaryEntry(models.Model):
    """
    Individual entries in a translation glossary
    """

    entry_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    glossary = models.ForeignKey(
        TranslationGlossary,
        on_delete=models.CASCADE,
        related_name='glossary_entries'
    )

    # Translation pair
    source_term = models.CharField(max_length=255)
    target_term = models.CharField(max_length=255)

    # Additional information
    notes = models.TextField(blank=True)
    part_of_speech = models.CharField(max_length=50, blank=True)

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['source_term']
        unique_together = ['glossary', 'source_term']

    def __str__(self):
        return f"{self.source_term} -> {self.target_term}"

    def record_usage(self):
        """
        Record usage of this glossary entry
        """
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class LanguagePair(models.Model):
    """
    Model for storing supported language pairs
    """

    pair_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)

    # Language names
    source_name = models.CharField(max_length=100)
    target_name = models.CharField(max_length=100)

    # Support information
    is_supported = models.BooleanField(default=True)
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.8
    )

    # Service availability
    google_translate = models.BooleanField(default=True)
    microsoft_translator = models.BooleanField(default=True)
    offline_models = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['source_language', 'target_language']
        indexes = [
            models.Index(fields=['source_language']),
            models.Index(fields=['target_language']),
            models.Index(fields=['is_supported']),
        ]

    def __str__(self):
        return f"{self.source_name} -> {self.target_name}"

    def get_available_services(self):
        """
        Get list of available translation services
        """
        services = []
        if self.google_translate:
            services.append('google_translate')
        if self.microsoft_translator:
            services.append('microsoft_translator')
        if self.offline_models:
            services.append('offline')
        return services
