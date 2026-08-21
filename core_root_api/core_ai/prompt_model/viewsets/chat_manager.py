from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from core_root_api.core_ai.prompt_model.models import PromptModel

class GetChatById(APIView):
    authentication_classes = []  # 🔓 No authentication
    permission_classes = []      # 🔓 No permission check

    def get(self, request):
        chat_id = request.query_params.get('chat_id')
        
        # Pagination parameters
        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 50))
        except ValueError:
            return Response({"status": False, "error": "Invalid pagination parameters"}, status=400)

        if not chat_id:
            return Response({
                "status": False,
                "error": "Missing required query parameter: chat_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            prompts_queryset = PromptModel.objects.filter(
                chat_id=chat_id
            ).select_related('user').order_by('time_created')

            if not prompts_queryset.exists():
                return Response({
                    "status": False,
                    "error": "No chat found with the given chat_id."
                }, status=status.HTTP_404_NOT_FOUND)

            paginator = Paginator(prompts_queryset, limit)
            page_obj = paginator.get_page(page)

            # Fetch the title efficiently
            title_obj = PromptModel.objects.filter(chat_id=chat_id).order_by('time_created').values('title').first()
            title = title_obj['title'] if title_obj and title_obj.get('title') else "Untitled Chat"

            # Build prompt data for the CURRENT PAGE only
            content = [
                {
                    "user_id": str(obj.user.public_id).replace('-', '') if obj.user else None,
                    "chat_id": obj.chat_id,
                    "prompt_in": obj.prompt_in,
                    "prompt_output": obj.prompt_output,
                    "updated": obj.updated,
                    "time_created": obj.time_created
                }
                for obj in page_obj
            ]

            return Response({
                "status": True,
                "data": {
                    "chat_id": chat_id,
                    "title": title,
                    "content": content,
                    "pagination": {
                        "current_page": page_obj.number,
                        "total_pages": paginator.num_pages,
                        "has_next": page_obj.has_next(),
                        "total_messages": paginator.count
                    }
                },
                "message": "Chat history retrieved successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "error": f"Internal server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
