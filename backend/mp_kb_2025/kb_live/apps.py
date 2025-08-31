"""Django app configuration for the kb_live application."""

from django.apps import AppConfig


class KbLiveConfig(AppConfig):
    """
    Configuration class for the kb_live application.

    This class defines configuration settings for the kettlebell live scoring and
    tracking application used during the Polish Kettlebell Championship 2025.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "kb_live"
