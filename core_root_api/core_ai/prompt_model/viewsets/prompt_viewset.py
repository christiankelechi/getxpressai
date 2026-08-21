from itertools import groupby
from django.utils.timezone import now
from django.db.models import Q
from operator import itemgetter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
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
from PIL import Image

import tempfile
import random
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from core_root_api.custom_api_urls import image_model_url
from functools import wraps
from rest_framework.response import Response

def require_post_data(keys):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_keys = [key for key in keys if key not in request.data]
            if missing_keys:
                return Response({
                    "status": False,
                    "message": f"Missing required fields: {', '.join(missing_keys)}"
                }, status=400)

            # Attach only the required data to request.validated_data
            request.validated_data = {key: request.data[key] for key in keys}
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator

def generate_chat_id(length=30):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class ChatPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from itertools import groupby
from operator import itemgetter

class ChatPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PromptViewset(viewsets.ModelViewSet):
    http_method_names = ['post', 'get','delete']
    serializer_class = PromptSerializer
    queryset = PromptModel.objects.all()
    pagination_class = ChatPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('filter', openapi.IN_QUERY, description="Filter type (today, yesterday, some_days_ago, last_month, long_time_ago)", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER)
        ]
    )
    def list(self, request):
        try:
            today = now().date()
            yesterday = today - timedelta(days=1)
            last_week = today - timedelta(days=7)
            last_month = today - timedelta(days=30)

            filters = {
                'today': Q(updated__date=today),
                'yesterday': Q(updated__date=yesterday),
                'some_days_ago': Q(updated__date__gt=last_week, updated__date__lt=today),
                'last_month': Q(updated__date__gt=last_month, updated__date__lt=last_week),
                'long_time_ago': Q(updated__date__lt=last_month)
            }

            filter_type = request.query_params.get('filter')
            base_queryset = PromptModel.objects.filter(user=request.user).order_by('chat_id', '-updated')

            if filter_type in filters:
                base_queryset = base_queryset.filter(filters[filter_type])

            page = self.paginate_queryset(base_queryset)

            if page is not None:
                # Instead of fetching all items, just group by chat_id
                # and return an empty content array to prevent crashes.
                prompts = [
                    {
                        "chat_id": obj.chat_id,
                        "updated": obj.updated
                    }
                    for obj in page
                ]

                # Group by chat_id
                grouped = {}
                for chat_id, group in groupby(prompts, key=itemgetter('chat_id')):
                    items = list(group)
                    title_obj = PromptModel.objects.filter(chat_id=chat_id, user=request.user).order_by('time_created').first()
                    grouped[chat_id] = {
                        "chat_id": chat_id,
                        "title": title_obj.title if title_obj else "Untitled Chat",
                        "content": [], # Empty content for scale, fetch details via GetChatById
                        "updated": items[0]["updated"] # Use first item's updated time for sorting
                    }

                # 🔽 Sort by the latest updated message
                sorted_chats = sorted(
                    grouped.values(),
                    key=lambda x: x["updated"],
                    reverse=True
                )

                paginated_response = self.get_paginated_response(sorted_chats).data

                return Response({
                    "status": True,
                    "data": paginated_response.get('results'),
                    "message": "Chat history grouped by chat ID retrieved successfully.",
                    "count": paginated_response.get('count'),
                    "next": paginated_response.get('next'),
                    "previous": paginated_response.get('previous')
                }, status=status.HTTP_200_OK)

            return Response({
                "status": True,
                "data": [],
                "message": "No chat data found."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "error": f"Internal server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                prompt_in = serializer.validated_data['prompt_in']
                new_chat = request.data.get('new_chat', False)
                emotion = request.data.get('emotion')
                if new_chat:
                    chat_id = generate_chat_id()
                else:
                    chat_id = request.data.get('chat_id')

                prompt_output = generate_answer(prompt_in, emotion=emotion)
                serializer.save(user=request.user, chat_id=chat_id,prompt_output=prompt_output)
                return Response(
                    {"status": True, "data": {"prompt_in": prompt_in, "prompt_output": prompt_output, "chat_id": chat_id,"new_chat":new_chat,"user_id":str(request.user.public_id).replace('-','')},
                     "message": "Message generated successfully"},
                    status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "error": f"Internal server error {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['patch'], url_path='rename-chat')
    @require_post_data(['chat_id', 'new_title'])
    def rename_chat(self, request):
        data = request.validated_data
        try:
            PromptModel.objects.filter(chat_id=data['chat_id'], user=request.user).update(title=data['new_title'])
            return Response({"status": True, "message": "Chat renamed successfully"})
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=500)
   
    @action(detail=False, methods=['post'], url_path='archive-chat')
    @require_post_data(['chat_id'])
    def archive_chat(self, request):
        data = request.validated_data
        try:
            PromptModel.objects.filter(chat_id=data['chat_id'], user=request.user).update(is_archived=True)
            return Response({"status": True, "message": "Chat archived successfully"})
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=500)
   
    @action(detail=False, methods=['delete'], url_path='delete-chat')
    def delete_chat(self, request):
        chat_id = request.query_params.get("chat_id")  # ✅ Query param for DELETE
        if not chat_id:
            return Response({"status": False, "error": "chat_id is required"}, status=400)

        try:
            PromptModel.objects.filter(chat_id=chat_id, user=request.user).delete()
            return Response({"status": True, "message": "Chat deleted successfully"})
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=500)
   
    @action(detail=False, methods=['patch'], url_path='share-chat')
    @require_post_data(['chat_id'])
    def share_chat(self, request):
        data = request.validated_data
        try:
            chat_data = PromptModel.objects.filter(
                chat_id=data['chat_id'],
                user=request.user
            ).values('prompt_in', 'prompt_output', 'updated', 'title')
            return Response({
                "status": True,
                "message": "Chat shared successfully",
                "data": list(chat_data)
            })
        except Exception as e:
            return Response({"status": False, "error": str(e)}, status=500)
#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('filter', openapi.IN_QUERY, description="Filter type (today, yesterday, some_days_ago, last_month, long_time_ago)", type=openapi.TYPE_STRING)
#         ]
#     )

 
    

#     def list(self, request):
#         try:
#             today = now().date()
#             yesterday = today - timedelta(days=1)
#             last_week = today - timedelta(days=7)
#             last_month = today - timedelta(days=30)

#             filters = {
#                 'today': Q(updated__date=today),
#                 'yesterday': Q(updated__date__gt=today),
#                 'some_days_ago': Q(updated__date__gt=last_week, updated__date__lt=today),
#                 'last_month': Q(updated__date__gt=last_month, updated__date__lt=last_week),
#                 'long_time_ago': Q(updated__date__lt=last_month)
#             }

#             filter_type = request.query_params.get('filter')
#             base_queryset = PromptModel.objects.filter(user=request.user)
#             if filter_type in filters:
#                 base_queryset = base_queryset.filter(filters[filter_type])

#             # Select only necessary fields
#             prompts = base_queryset.values(
#                 'chat_id', 'prompt_in', 'prompt_output', 'updated'
#             ).order_by('chat_id')

#             # Group by chat_id using itertools.groupby
#             grouped_chats = {
#                 chat_id: list(group)
#                 for chat_id, group in groupby(prompts, key=itemgetter('chat_id'))
#             }

#             return Response({
#                 "status": True,
#                 "data": grouped_chats,
#                 "message": "Chat history grouped by chat ID retrieved successfully."
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 "status": False,
#                 "error": f"Internal server error: {str(e)}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageInsightsViewset(viewsets.ModelViewSet):
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
            
            # For MVP, mock the response since heavy ML is removed
            result = "This image appears to show an enthusiastic learner! (Mocked response for MVP)"
            
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