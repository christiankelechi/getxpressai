from rest_framework import serializers
from core_root_api.core_ai.prompt_model.models import PromptModel
from core_root_api.core_ai.prompt_model.models import Images
# serializers.py


class PromptDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PromptModel
        fields = '__all__'

class PromptSerializer(serializers.ModelSerializer):
    new_chat=serializers.BooleanField(write_only=True)
    class Meta:
        model = PromptModel
        exclude = ['user', 'prompt_output']


class ImageSerializer(serializers.ModelSerializer):
    image_file = serializers.ImageField(allow_null=True, required=False)

    def to_representation(self, instance):
        """Customize the response to include the default image URL if `profile_image` is not uploaded."""
        data = super().to_representation(instance)
        # if not instance.image_file:
        #     data['profile_image'] = "https://res.cloudinary.com/drlcmhrcg/image/upload/v1739003221/vurzoqjwqft4zofkwdp3.png"
        return data

    class Meta:
        model=Images
        fields="__all__"
    


class VideoSerializer(serializers.ModelSerializer):
    prompt_in = serializers.ImageField(allow_null=True, required=False)
