
from rest_framework import viewsets
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from core_root_api.core_ai.prompt_model.models import PromptModel
from core_root_api.core_ai.prompt_model.serializers.prompt_serializer import PromptSerializer,ImageSerializer
from rest_framework.response import Response
from rest_framework import status
from core_root_api.core_ai.prompt_model.utils.chat_message import generate_answer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import string
from gradio_client import Client, handle_file

from PIL import Image

from gradio_client import Client, handle_file



import tempfile
import random
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core_root_api.custom_api_urls import image_model_url


class VideoGenerator(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImageSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            # Save the uploaded image; this creates an Images object.
            image_instance = serializer.save()
            
            # Retrieve the exact URL from the saved instance.
            # (Make sure your CloudinaryField is configured to provide a URL.)
            image_url = image_instance.image_file.url
            if not image_url:
                return Response({
                    "status": False,
                    "error": "Could not retrieve image URL."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use gradio_client's handle_file to prepare the file using the URL.
            file_input = handle_file(image_url)
            
            # Initialize the Gradio Client using your space identifier.
            client = Client("christiankeleze/xpressimagemodel")
            # Call the predict endpoint.
            result = client.predict(image=file_input, api_name="/predict")
            
            return Response({
                "status": True,
                "message": "Image analysed successfully",
                "data": result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "error": "Internal server error: " + str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)