from django.db.models.signals import post_save
from django.dispatch import receiver
from core_root_api.core_ai.prompt_model.models import PromptModel
from core_root_api.core_ai.prompt_model.utils.chat_message import clean_text, generate_answer  # Or Gemini wrapper
from django.db.models import Count

@receiver(post_save, sender=PromptModel)
def generate_chat_title_signal(sender, instance, created, **kwargs):
    if not created:
        return

    # Only generate title if this is the first message in the chat
    chat_count = PromptModel.objects.filter(chat_id=instance.chat_id).count()
    if chat_count > 1 or instance.chat_id is None:
        return

    try:
        prompt_text = instance.prompt_in.strip()
        title_prompt = f"Give a very short,direct, clear title for this prompt: {prompt_text}"
        title =clean_text(generate_answer(title_prompt))

        # Trim if it's too long
        if len(title) > 100:
            title = title[:100]

        # Save title to the first prompt
        PromptModel.objects.filter(id=instance.id).update(title=title)

    except Exception as e:
        # Log or silently fail to avoid blocking other ops
        print(f"[Signal] Error generating chat title: {e}")
