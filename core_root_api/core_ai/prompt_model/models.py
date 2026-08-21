from django.db import models
from core_root_api.security.user.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class PromptModel(models.Model):
    chat_id=models.TextField(null=True,blank=True)
    title = models.TextField(blank=True, null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    prompt_in=models.TextField(null=True,blank=True)
    prompt_output=models.TextField(null=True,blank=True)
    time_created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    new_chat=models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['chat_id', '-updated']),
        ]

    def __str__(self):
        return f"{self.user} prompts to the text model"

class Images(models.Model):
    image_file=CloudinaryField("imageprompt",null=True,blank=True)
    
    