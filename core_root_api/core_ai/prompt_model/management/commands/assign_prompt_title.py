from django.core.management.base import BaseCommand
from core_root_api.core_ai.prompt_model.models import PromptModel
from core_root_api.core_ai.prompt_model.utils.chat_message import clean_text, generate_answer
from django.db.models import Q
from collections import defaultdict
import time
import os

class Command(BaseCommand):
    help = 'Assigns missing titles to chat groups using Gemini'

    def handle(self, *args, **kwargs):
        try:
            all_prompt_sets = PromptModel.objects.filter(
                Q(title__isnull=True) | Q(title='')
            ).order_by('chat_id', 'time_created')

            grouped_prompts = defaultdict(list)
            for prompt in all_prompt_sets:
                grouped_prompts[prompt.chat_id].append(prompt)

            updated_count = 0
            failed_count = 0
            delay_seconds = 10  # delay to avoid quota exhaustion
            log_file = "success.txt"

            for chat_id, prompt_list in grouped_prompts.items():
                try:
                    first_prompt = prompt_list[0]
                    if not first_prompt.title:
                        prompt_text = first_prompt.prompt_output or first_prompt.prompt_in
                        title_prompt = f"give very short title of this prompt so i can use it as title of the chat just few words: {prompt_text}"
                        title = clean_text(generate_answer(title_prompt))

                        if title:
                            first_prompt.title = title.strip()[:100]  # avoid DB overflow
                            first_prompt.save()
                            updated_count += 1
                            self.stdout.write(self.style.SUCCESS(f"✅ Title updated for chat_id {chat_id}: {title}"))
                        time.sleep(delay_seconds)  # throttle to avoid API limits
                except Exception as sub_e:
                    failed_count += 1
                    self.stderr.write(self.style.ERROR(f"⚠️ Skipped chat_id {chat_id} due to error: {str(sub_e)}"))

            # Final status logging
            if failed_count == 0:
                with open(log_file, "w") as f:
                    f.write(f"✅ Completed title assignation. Titles updated for {updated_count} chat(s).\n")
                self.stdout.write(self.style.SUCCESS(f"\n🎉 Titles assigned. Success logged in {log_file}"))
            else:
                with open("failed.txt", "w") as f:
                    f.write(f"❌ Could not finish all. {updated_count} succeeded, {failed_count} failed.\n")
                self.stderr.write(self.style.ERROR(f"\n❌ Some errors occurred. Details in failed.txt"))

        except Exception as e:
            with open("failed.txt", "w") as f:
                f.write(f"❌ Could not finish due to fatal error: {str(e)}\n")
            self.stderr.write(self.style.ERROR(f"❌ Fatal error during processing: {str(e)}"))
