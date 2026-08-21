from rest_framework import viewsets
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from core_root_api.security.user.models import User
from core_root_api.security.auth.serializer.google_auth import GoogleAuthSerializer

class GoogleAuthViewSet(viewsets.ModelViewSet):
    serializer_class = GoogleAuthSerializer
    http_method_names = ['post', 'get']
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid():
                email = serializer.validated_data['email']
                social_user_id = serializer.validated_data['social_user_id']
                profile_image = serializer.validated_data['profile_image']
                name = serializer.validated_data['name']

                # Try to fetch existing user by email
                user = User.objects.filter(email=email).first()

                if user:
                    if user.social_user_id and user.social_user_id != social_user_id:
                        # Conflict: Another social account tried to use existing email
                        return Response({
                            "status": False,
                            "error_message": "Email is already associated with another account."
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Update existing user to a Google user
                    user.social_user_id = social_user_id
                    user.profile_image = profile_image
                    user.full_name = name
                    user.save()
                    social_user = user
                    created = False
                else:
                    # If no user exists, create a new Google user
                    social_user, created = User.objects.get_or_create_social_user(
                        email=email,
                        social_user_id=social_user_id,
                        profile_image=profile_image,
                        full_name=name
                    )

                # Ensure fields are up-to-date
                updated = False
                if social_user.profile_image != profile_image:
                    social_user.profile_image = profile_image
                    updated = True
                if social_user.full_name != name:
                    social_user.full_name = name
                    updated = True
                if updated:
                    social_user.save()

                # Generate JWT tokens
                refresh = RefreshToken.for_user(social_user)

                return Response({
                    "data": {
                        "user": {
                            "id": str(social_user.public_id).replace("-", ""),
                            "full_name": social_user.full_name,
                            "username": social_user.username,
                            "profile_image": (
                                social_user.profile_image if isinstance(social_user.profile_image, str)
                                else social_user.profile_image.url if social_user.profile_image else None
                            ),
                            "email": social_user.email,
                            "is_active": social_user.is_active,
                            "created": social_user.created,
                            "updated": social_user.updated,
                        },
                        "refresh_token": str(refresh),
                        "access_token": str(refresh.access_token),
                    },
                    "message": "Google Login successful",
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": False,
                "error_message": "Invalid data.",
                "details": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "error_message": f"Something went wrong: {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class GoogleAuthViewSet(viewsets.ModelViewSet):
#     serializer_class = GoogleAuthSerializer
#     http_method_names = ['post', 'get']
#     permission_classes = [AllowAny]

#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         try:
#             if serializer.is_valid():
#                 email = serializer.validated_data['email']
#                 social_user_id = serializer.validated_data['social_user_id']
#                 profile_image = serializer.validated_data['profile_image']
#                 name = serializer.validated_data['name']
#                 # Always use the custom get_or_create method
#                 social_user, created = User.objects.get_or_create_social_user(
#                     email=email,
#                     social_user_id=social_user_id,
#                     profile_image=profile_image,
#                     full_name=name
#                 )

#                 # Update profile image in real-time every login
#                 if social_user.profile_image != profile_image or social_user.full_name != name or social_user.social_user_id!=social_user_id:
#                     social_user.profile_image = profile_image
#                     social_user.full_name=name
#                     # social_user.social_user_id=social_user_id,

#                     social_user.save()

#                 # Generate JWT tokens
#                 refresh = RefreshToken.for_user(social_user)

#                 return Response({
#                     "data": {
#                         "user": {
#                             "id": str(social_user.public_id).replace("-", ""),
#                             "full_name": social_user.full_name,
#                             # "name": social_user.name,
#                             "username": social_user.username,
#                             "profile_image": social_user.profile_image if isinstance(social_user.profile_image, str) else social_user.profile_image.url,
#                             "email": social_user.email,
#                             "is_active": social_user.is_active,
#                             "created": social_user.created,
#                             "updated": social_user.updated,
#                         },
#                         "refresh_token": str(refresh),
#                         "access_token": str(refresh.access_token),
#                     },
#                     "message": "Google Login successful",
#                 }, status=status.HTTP_201_CREATED)

#             return Response({
#                 "status": False,
#                 "error_message": "Invalid data.",
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({
#                 "status": False,
#                 "error_message": f"Something went wrong: {e}"
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # def create(self, request):
    #     serializer = self.serializer_class(data=request.data)
    #     try:
    #         if serializer.is_valid():
    #             email = serializer.validated_data['email']
    #             social_user_id=serializer.validated_data['social_user_id']
    #             profile_image=serializer.validated_data['profile_image']
    #             name=serializer.validated_data['name']
    #             current_user=User.objects.filter(social_user_id=social_user_id,email=email).first()
    #             if current_user:
    #                 social_user, created = User.objects.get_or_create_social_user(email=email, social_user_id=social_user_id,profile_image=profile_image,full_name=name)
    #                 social_user.profile_image.url=profile_image
    #                 social_user.save()
    #                 # Generate JWT tokensf
    #                 refresh = RefreshToken.for_user(social_user)
                    
                    
    #                 return Response(
    #                     # "id": str(social_user.public_id).replace("-", ""),
                        
    #                     {"data":{
                        
    #                     "user": {
    #                         "id": str(social_user.public_id).replace("-", ""),
    #                         "full_name":social_user.full_name,
    #                         "name": social_user.name,
    #                         "username": social_user.username,
    #                         "profile_image":social_user.profile_image.url,
    #                         "email": social_user.email,
    #                         "is_active": social_user.is_active,
    #                         "created": social_user.created,
    #                         "updated": social_user.updated,
    #                     },
    #                     "refresh": str(refresh),
    #                     "token": str(refresh.access_token),
    #                     },
    #                     # "status": True,
    #                     "message": "google Login successful",
    #                 }, status=status.HTTP_201_CREATED)
    #                 # return Response({
    #                 #     "status": False,
    #                 #     "error_message": "User have already signed up, login",
    #                 #     }, status=status.HTTP_400_BAD_REQUEST)
    #             else:
                    
                
    #             # Use the custom method from UserManager
    #                 social_user, created = User.objects.get_or_create_social_user(email=email, social_user_id=social_user_id,profile_image=profile_image,full_name=name)

    #                 social_user.profile_image=profile_image
    #                 social_user.save()
    #                 # Generate JWT tokensf
    #                 refresh = RefreshToken.for_user(social_user)
                    
                    
    #                 return Response(
    #                     # "id": str(social_user.public_id).replace("-", ""),
                        
    #                     {"data":{
                        
    #                     "user": {
    #                        "id": str(social_user.public_id).replace("-", ""),
    #                         "full_name":social_user.full_name,
    #                         "name": social_user.name,
    #                         "username": social_user.username,
    #                         "profile_image":social_user.profile_image.url,
    #                         "email": social_user.email,
    #                         "is_active": social_user.is_active,
    #                         "created": social_user.created,
    #                         "updated": social_user.updated,
    #                     },
    #                     "refresh": str(refresh),
    #                     "token": str(refresh.access_token),
    #                     },
    #                     # "status": True,
    #                     "message": "google Login successful",
    #                 }, status=status.HTTP_201_CREATED)

    #             return Response({
    #                 "status": False,
    #                 "error_message": "Invalid data.",
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #         return Response({
    #                 "status": False,
    #                 "error_message": "Invalid data.",
    #             }, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({
    #             "status": False,
    #             "error_message": f"Email already exist {e}"
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)