"""
XPRESSAI Video Engine - Video URLs
URL patterns for video generation API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.video_views import (
    VideoGenerationProjectViewSet,
    VideoSegmentViewSet,
    VideoTemplateViewSet,
    VideoProcessingQueueViewSet
)

# Create a router for the video API
router = DefaultRouter()

# Register viewsets with the router
router.register(r'projects', VideoGenerationProjectViewSet, basename='video-projects')
router.register(r'segments', VideoSegmentViewSet, basename='video-segments')
router.register(r'templates', VideoTemplateViewSet, basename='video-templates')
router.register(r'queue', VideoProcessingQueueViewSet, basename='video-queue')

app_name = 'video'

# URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),

    # Custom endpoints for video generation
    path('projects/<uuid:project_id>/generate/',
         VideoGenerationProjectViewSet.as_view({'post': 'start_generation'}),
         name='project-generate'),

    path('projects/<uuid:project_id>/cancel/',
         VideoGenerationProjectViewSet.as_view({'post': 'cancel_generation'}),
         name='project-cancel'),

    path('projects/<uuid:project_id>/download/',
         VideoGenerationProjectViewSet.as_view({'get': 'download_video'}),
         name='project-download'),

    path('projects/<uuid:project_id>/status/',
         VideoGenerationProjectViewSet.as_view({'get': 'status'}),
         name='project-status'),

    path('projects/<uuid:project_id>/duplicate/',
         VideoGenerationProjectViewSet.as_view({'post': 'duplicate'}),
         name='project-duplicate'),

    # Segment management endpoints
    path('segments/<uuid:segment_id>/regenerate/',
         VideoSegmentViewSet.as_view({'post': 'regenerate'}),
         name='segment-regenerate'),

    # Template endpoints
    path('templates/<uuid:template_id>/use/',
         VideoTemplateViewSet.as_view({'post': 'use_template'}),
         name='template-use'),

    # Queue management endpoints
    path('queue/stats/',
         VideoProcessingQueueViewSet.as_view({'get': 'stats'}),
         name='queue-stats'),

    # Bulk operations
    path('projects/bulk-delete/',
         VideoGenerationProjectViewSet.as_view({'post': 'bulk_delete'}),
         name='bulk-delete'),

    path('projects/bulk-export/',
         VideoGenerationProjectViewSet.as_view({'post': 'bulk_export'}),
         name='bulk-export'),
]
