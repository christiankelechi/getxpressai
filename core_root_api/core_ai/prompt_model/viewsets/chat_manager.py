from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core_root_api.core_ai.prompt_model.models import PromptModel  # adjust import to your app

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core_root_api.core_ai.prompt_model.models import PromptModel
from itertools import groupby
from operator import itemgetter
from django.utils.timezone import now
from django.db.models import Q

class GetChatById(APIView):
    authentication_classes = []  # 🔓 No authentication
    permission_classes = []      # 🔓 No permission check

    def get(self, request):
        chat_id = request.query_params.get('chat_id')
        if not chat_id:
            return Response({
                "status": False,
                "error": "Missing required query parameter: chat_id"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            prompts_queryset = PromptModel.objects.filter(chat_id=chat_id).order_by('-updated')

            if not prompts_queryset.exists():
                return Response({
                    "status": False,
                    "error": "No chat found with the given chat_id."
                }, status=status.HTTP_404_NOT_FOUND)

            # Build prompt data
            prompts = [
                {
                    "user_id": str(obj.user.public_id).replace('-', ''),
                    "chat_id": obj.chat_id,
                    "prompt_in": obj.prompt_in,
                    "prompt_output": obj.prompt_output,
                    "updated": obj.updated
                }
                for obj in prompts_queryset
            ]

            # Group by chat_id (only one group expected)
            grouped = {}
            for cid, group in groupby(prompts, key=itemgetter('chat_id')):
                items = list(group)
                title_obj = prompts_queryset.order_by('time_created').first()
                grouped[cid] = {
                    "chat_id": cid,
                    "title": title_obj.title if title_obj else "Untitled Chat",
                    "content": items
                }

            chat_data = list(grouped.values())[0]  # Only one chat_id group

            return Response({
                "status": True,
                "data": chat_data,
                "message": "Chat history retrieved successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": False,
                "error": f"Internal server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
