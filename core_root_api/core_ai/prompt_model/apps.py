from django.apps import AppConfig


class PromptModelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_root_api.core_ai.prompt_model"
    label="core_root_api_core_ai_prompt_model"

    def ready(self):
        import core_root_api.core_ai.prompt_model.signals
