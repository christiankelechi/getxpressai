from rest_framework import routers
from django.urls import path
from core_root_api.core_ai.prompt_model.viewsets.chat_manager import GetChatById
from core_root_api.core_ai.prompt_model.viewsets.prompt_viewset  import PromptViewset,ImageInsightsViewset
from core_root_api.core_ai.prompt_model.viewsets.prompt_suggestion  import PromptSuggestionsViewset


router=routers.SimpleRouter()
router.register(r'prompt',PromptViewset,basename='prompt')



urlpatterns=[
    *router.urls,
    path('prompt-suggestions/',PromptSuggestionsViewset.as_view({"get":"list"}),name='prompt_suggestions'),
    path('image/insights/',ImageInsightsViewset.as_view({"post":"create"}),name='image_insight'),
    path('chat/chat-id/', GetChatById.as_view(), name='get-chat-by-id'),
]
