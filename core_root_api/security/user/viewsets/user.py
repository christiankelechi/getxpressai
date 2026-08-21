# from rest_framework.permissions import IsAuthenticated
# from rest_framework import viewsets
# from django.core.exceptions import ObjectDoesNotExist
# from core_root_api.security.user.serializers.user import UserSerializer
# from core_root_api.security.user.models import User
# from rest_framework import status

# from rest_framework.response import Response
# class UserViewset(viewsets.ModelViewSet):
#     http_method_names=['patch','get','delete']
#     permission_classes=[IsAuthenticated,]
#     serializer_class=UserSerializer

#     def get_queryset(self):
#         if self.request.user.is_superuser:
#             return User.objects.exclude(is_superuser=True)
#         return User.objects.exclude(is_superuser=True)
    
#     def get_object(self):
#         obj=User.objects.get_object_by_public_id(self.kwargs['pk'])
#         self.check_object_permissions(self.request,obj)
#         return obj

#     def destroy(self, request, *args, **kwargs):
#         user_id = self.kwargs.get("pk")  # UUID from URL
#         request_email = self.request.user.email

#         try:
#             user = User.objects.get(public_id=user_id)  # Adjust if using `id` instead of `public_id`

#             if user.email != request_email:
#                 return Response({
#                     "error": "Unauthorized action. You are only permitted to delete your own account.",
#                 }, status=status.HTTP_403_FORBIDDEN)

#             user.delete()
#             return Response({
#                 "message": f"Your account with email '{request_email}' has been successfully deleted.","data":None
#             }, status=status.HTTP_200_OK)

#         except User.DoesNotExist:
#             return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from core_root_api.security.user.serializers.user import UserSerializer
from core_root_api.security.user.models import User

class UserViewset(viewsets.ModelViewSet):
    http_method_names = ['patch', 'get', 'delete']
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.exclude(is_superuser=True)
        return User.objects.exclude(is_superuser=True)

    def get_object(self):
        obj = User.objects.get_object_by_public_id(self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        user_id = self.kwargs.get("pk")
        request_email = self.request.user.email

        try:
            user = User.objects.get(public_id=user_id)
            
            if user.email != request_email:
                return Response({
                    "error": "Unauthorized action. You are only permitted to delete your own account.",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

            user.delete()
            return Response({
                "message": f"Your account with email '{request_email}' has been successfully deleted.",
                "data": None
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                "error": "User not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Ensure any unexpected error returns a proper Response
            return Response({
                "error": "An unexpected error occurred.",
                "data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
