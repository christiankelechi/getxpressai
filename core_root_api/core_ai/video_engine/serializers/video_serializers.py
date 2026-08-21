"""
XPRESSAI Video Engine - Video Serializers
Data serialization for video generation API
"""

from rest_framework import serializers
from django.utils import timezone
from ..models.video_models import (
    VideoGenerationProject,
    VideoSegment,
    VideoTemplate,
    VideoProcessingQueue
)


class VideoGenerationProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for video generation projects
    """
    segments_count = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    processing_duration_display = serializers.SerializerMethodField()

    class Meta:
        model = VideoGenerationProject
        fields = [
            'project_id', 'title', 'description', 'status', 'prompt',
            'duration', 'ai_model', 'model_version', 'resolution',
            'language', 'target_languages', 'voice_type', 'custom_voice',
            'video_file', 'thumbnail', 'processing_started_at',
            'processing_completed_at', 'processing_duration',
            'processing_duration_display', 'quality_score', 'file_size',
            'error_message', 'retry_count', 'created_at', 'updated_at',
            'segments_count', 'video_url'
        ]
        read_only_fields = [
            'project_id', 'created_at', 'updated_at', 'processing_started_at',
            'processing_completed_at', 'processing_duration', 'file_size',
            'segments_count', 'video_url', 'processing_duration_display'
        ]

    def get_segments_count(self, obj):
        return obj.segments.count()

    def get_video_url(self, obj):
        return obj.get_video_url()

    def get_processing_duration_display(self, obj):
        duration = obj.get_processing_time()
        if duration:
            total_seconds = int(duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            return "02d"
        return None


class VideoSegmentSerializer(serializers.ModelSerializer):
    """
    Serializer for video segments
    """
    project_title = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = VideoSegment
        fields = [
            'segment_id', 'project', 'project_title', 'title', 'order',
            'prompt', 'duration', 'ai_model', 'video_file', 'audio_file',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['segment_id', 'created_at', 'updated_at']


class VideoTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for video templates
    """
    usage_count = serializers.IntegerField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = VideoTemplate
        fields = [
            'template_id', 'name', 'description', 'template_config',
            'category', 'tags', 'usage_count', 'rating', 'created_by',
            'created_by_username', 'is_public', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'template_id', 'created_at', 'updated_at', 'usage_count'
        ]


class VideoProcessingQueueSerializer(serializers.ModelSerializer):
    """
    Serializer for processing queue items
    """
    project_title = serializers.CharField(source='project.title', read_only=True)
    user_username = serializers.CharField(source='project.user.username', read_only=True)
    queue_wait_time = serializers.SerializerMethodField()

    class Meta:
        model = VideoProcessingQueue
        fields = [
            'queue_id', 'project', 'project_title', 'user_username',
            'priority', 'position', 'processing_node', 'gpu_required',
            'status', 'queued_at', 'processing_started_at',
            'completed_at', 'queue_wait_time'
        ]
        read_only_fields = ['queue_id', 'queued_at', 'processing_started_at', 'completed_at']

    def get_queue_wait_time(self, obj):
        return obj.get_queue_wait_time()


class VideoGenerationRequestSerializer(serializers.Serializer):
    """
    Serializer for video generation requests
    """
    title = serializers.CharField(max_length=200, required=True)
    prompt = serializers.CharField(required=True)
    duration = serializers.IntegerField(min_value=5, max_value=300, default=30)
    ai_model = serializers.ChoiceField(
        choices=['stable-diffusion-video', 'sora', 'runway-ml'],
        default='stable-diffusion-video'
    )
    resolution = serializers.ChoiceField(
        choices=['480p', '720p', '1080p', '4k'],
        default='720p'
    )
    language = serializers.CharField(max_length=10, default='en')
    voice_type = serializers.ChoiceField(
        choices=['default', 'male', 'female', 'neutral'],
        default='default'
    )
    target_languages = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False,
        default=list
    )

    def validate_prompt(self, value):
        """
        Validate prompt content
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Prompt must be at least 10 characters long")
        if len(value.strip()) > 2000:
            raise serializers.ValidationError("Prompt must not exceed 2000 characters")
        return value.strip()


class VideoProjectUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating video projects
    """
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    prompt = serializers.CharField(required=False)
    duration = serializers.IntegerField(min_value=5, max_value=300, required=False)
    ai_model = serializers.CharField(max_length=100, required=False)
    resolution = serializers.CharField(max_length=20, required=False)
    language = serializers.CharField(max_length=10, required=False)
    voice_type = serializers.CharField(max_length=50, required=False)


class BulkVideoOperationSerializer(serializers.Serializer):
    """
    Serializer for bulk video operations
    """
    project_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True
    )
    operation = serializers.ChoiceField(
        choices=['delete', 'regenerate', 'export'],
        required=True
    )


class VideoAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for video analytics requests
    """
    project_id = serializers.UUIDField(required=True)
    metrics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=['views', 'engagement', 'performance']
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class VideoStatusResponseSerializer(serializers.Serializer):
    """
    Serializer for video status responses
    """
    project_id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.IntegerField(min_value=0, max_value=100)
    message = serializers.CharField(required=False)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    processing_started_at = serializers.DateTimeField(required=False)
    processing_completed_at = serializers.DateTimeField(required=False)
    processing_duration = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)
