from rest_framework import viewsets
from rest_framework import viewsets
from core_root_api.core_ai.prompt_model.models import PromptModel
from core_root_api.core_ai.prompt_model.serializers.prompt_serializer import PromptSerializer
from rest_framework.response import Response
from rest_framework import status
from core_root_api.core_ai.prompt_model.utils.chat_message import generate_answer
from rest_framework import viewsets, status
from rest_framework.response import Response
from core_root_api.core_ai.prompt_model.utils.chat_message import generate_answer

class PromptSuggestionsViewset(viewsets.ViewSet):
    http_method_names = ['get']

    def list(self, request):
        try:
            # Define a single prompt that instructs the AI to generate a random chat suggestion,
            # explicitly avoiding love-related topics.
            suggestions= (
                "Suggest ways to incorporate AI into the classroom effectively.",
                "Help me create a learning plan",
                "Give me a quick tutorial on using React",
                "How can I balance learning with a busy schedule?"

            )
        
            
            return Response({
                "status": True,
                "data": suggestions,
                "message": "Suggestions returned successfully"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

