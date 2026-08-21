# XPRESSAI VIDEO GENERATION URLS - ENGLISH PSEUDO CODE
# URL patterns for video generation API endpoints

# STEP 1: Import Django URL modules
# We need path and include for URL configuration
# DefaultRouter for automatic API URL generation

# STEP 2: Import our viewsets
# These will be registered with the router

# STEP 3: Create the main API router
# This will automatically generate URLs for our ViewSets

# STEP 4: Register ViewSets with the router
# Each ViewSet gets its own URL namespace

# VideoGenerationProjectViewSet URLs:
# - GET /api/video/projects/ - List user's projects
# - POST /api/video/projects/ - Create new project
# - GET /api/video/projects/{id}/ - Get project details
# - PUT /api/video/projects/{id}/ - Update project
# - DELETE /api/video/projects/{id}/ - Delete project

# VideoSegmentViewSet URLs:
# - GET /api/video/segments/ - List segments (with project filter)
# - POST /api/video/segments/ - Create new segment
# - GET /api/video/segments/{id}/ - Get segment details
# - PUT /api/video/segments/{id}/ - Update segment
# - DELETE /api/video/segments/{id}/ - Delete segment

# VoiceProfileViewSet URLs:
# - GET /api/video/voice-profiles/ - List user's voice profiles
# - POST /api/video/voice-profiles/ - Create new voice profile
# - GET /api/video/voice-profiles/{id}/ - Get voice profile details
# - PUT /api/video/voice-profiles/{id}/ - Update voice profile
# - DELETE /api/video/voice-profiles/{id}/ - Delete voice profile

# TranslationRequestViewSet URLs:
# - GET /api/video/translations/ - List translation requests
# - POST /api/video/translations/ - Create translation request
# - GET /api/video/translations/{id}/ - Get translation details

# VideoAnalyticsViewSet URLs:
# - GET /api/video/analytics/ - List video analytics
# - GET /api/video/analytics/{id}/ - Get specific analytics

# EmotionDetectionResultViewSet URLs:
# - GET /api/video/emotions/ - List emotion detection results
# - GET /api/video/emotions/{id}/ - Get specific emotion result

# STEP 5: Define custom URL patterns
# These are additional endpoints beyond standard CRUD

# Project-specific custom URLs:
# - POST /api/video/projects/{project_id}/generate/ - Start video generation
# - POST /api/video/projects/{project_id}/cancel/ - Cancel video generation
# - GET /api/video/projects/{project_id}/download/ - Download completed video
# - POST /api/video/projects/{project_id}/analyze-emotions/ - Start emotion analysis
# - GET /api/video/projects/{project_id}/status/ - Get detailed project status
# - POST /api/video/projects/{project_id}/duplicate/ - Duplicate project
# - GET /api/video/projects/{project_id}/preview/ - Get video preview

# Segment-specific custom URLs:
# - POST /api/video/segments/{segment_id}/regenerate/ - Regenerate segment
# - GET /api/video/segments/{segment_id}/preview/ - Preview segment
# - POST /api/video/segments/{segment_id}/reorder/ - Change segment order

# Voice profile custom URLs:
# - POST /api/video/voice-profiles/{profile_id}/upload-audio/ - Upload training audio
# - POST /api/video/voice-profiles/{profile_id}/start-training/ - Start voice training
# - GET /api/video/voice-profiles/{profile_id}/progress/ - Get training progress
# - POST /api/video/voice-profiles/{profile_id}/test/ - Test voice profile

# Translation custom URLs:
# - GET /api/video/translations/supported-languages/ - List supported languages
# - POST /api/video/translations/{request_id}/retry/ - Retry failed translation
# - GET /api/video/translations/{request_id}/preview/ - Preview translation

# STEP 6: Define bulk operation URLs
# These handle multiple items at once

# Bulk project operations:
# - POST /api/video/projects/bulk-delete/ - Delete multiple projects
# - POST /api/video/projects/bulk-generate/ - Start generation for multiple projects
# - POST /api/video/projects/bulk-export/ - Export multiple projects

# Bulk segment operations:
# - POST /api/video/segments/bulk-regenerate/ - Regenerate multiple segments
# - POST /api/video/segments/bulk-delete/ - Delete multiple segments

# STEP 7: Define search and filter URLs
# These provide advanced querying capabilities

# Search URLs:
# - GET /api/video/projects/search/ - Search projects by title/description
# - GET /api/video/voice-profiles/search/ - Search voice profiles
# - GET /api/video/templates/search/ - Search video templates

# Filter URLs:
# - GET /api/video/projects/filter/ - Filter projects by status/date/etc
# - GET /api/video/analytics/filter/ - Filter analytics by date range
# - GET /api/video/emotions/filter/ - Filter emotions by type/confidence

# STEP 8: Define export URLs
# These handle data export operations

# Export URLs:
# - GET /api/video/projects/export/ - Export projects to CSV/JSON
# - GET /api/video/analytics/export/ - Export analytics data
# - GET /api/video/emotions/export/ - Export emotion data

# STEP 9: Define webhook URLs
# These handle external service integrations

# Webhook URLs:
# - POST /api/video/webhooks/video-completed/ - Handle video completion notifications
# - POST /api/video/webhooks/training-completed/ - Handle training completion
# - POST /api/video/webhooks/payment-success/ - Handle payment notifications

# STEP 10: Define admin URLs
# These are for administrative operations

# Admin URLs:
# - GET /api/video/admin/stats/ - Get system-wide statistics
# - POST /api/video/admin/cleanup/ - Clean up old files/data
# - GET /api/video/admin/queue/ - View processing queue status
# - POST /api/video/admin/queue/clear/ - Clear processing queue

# STEP 11: Define public URLs
# These don't require authentication

# Public URLs:
# - GET /api/video/templates/public/ - List public templates
# - GET /api/video/templates/{id}/public/ - View public template details
# - POST /api/video/contact/ - Contact form for support

# STEP 12: Include router URLs in main urlpatterns
# This makes all the ViewSet URLs available

# STEP 13: Define URL namespaces
# Use app_name for URL reversing in templates

# STEP 14: Add URL patterns for different API versions
# Support multiple API versions for backward compatibility

# API Version URLs:
# - /api/v1/video/ - Version 1 of the API
# - /api/v2/video/ - Version 2 with new features
# - /api/latest/video/ - Always points to latest version

# STEP 15: Define error handling URLs
# Custom error pages and handling

# Error URLs:
# - /api/video/404/ - Custom 404 handler
# - /api/video/500/ - Custom 500 handler
# - /api/video/rate-limit/ - Rate limit exceeded handler
