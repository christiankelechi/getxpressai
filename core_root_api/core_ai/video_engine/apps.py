"""
XPRESSAI Video Engine App Configuration
Django app configuration for video generation system
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VideoEngineConfig(AppConfig):
    """
    Configuration for the XPRESSAI Video Engine app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_root_api.core_ai.video_engine'
    verbose_name = _('XPRESSAI Video Engine')

    def ready(self):
        """
        Initialize the video engine app when Django starts
        """
        # Import signals and startup tasks
        try:
            from . import signals
        except ImportError:
            pass

        # Initialize services if needed
        self._initialize_services()

    def _initialize_services(self):
        """
        Initialize AI services and models
        """
        # This will be called when Django starts
        # Initialize any background services here
        pass
