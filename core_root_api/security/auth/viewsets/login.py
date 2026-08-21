# from rest_framework.response import Response
# from rest_framework.viewsets import ViewSet
# from rest_framework.permissions import AllowAny
# from rest_framework import status
# from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
# from core_root_api.security.auth.serializer.login import LoginSerializerClass
# from rest_framework import viewsets
# from core_root_api.security.user.models import User
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import BasicAuthentication
# from django.http import HttpResponseRedirect
# from core_root_api.security import base_url
# import datetime
# import time
# import platform

# class LoginViewSet(viewsets.ModelViewSet):
#     serializer_class = LoginSerializerClass
#     permission_classes = (AllowAny,)
#     http_method_names = ['post']

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.serializer_class(data=request.data)
#             # print(serializer)
            
            
#             if serializer.is_valid():
#                 valid_user=User.objects.get(email=str(serializer.initial_data['email']))
                
#                 if valid_user.is_active==False:
#                     return Response({"error":"You have to activate your account first","status":False}, status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     return Response({"data":serializer.validated_data,"message":"Login Successful"}, status=status.HTTP_200_OK)
#                     # return HttpResponseRedirect(f"{base_url.main_url}/library/dashboard/")
#             else:
#                 return Response({'error':'User  with that email or password does not exist','status':False},status=status.HTTP_401_UNAUTHORIZED)

#         except:
            
#             return Response({'error':'User  with that email or password does not exist','status':False},status=status.HTTP_401_UNAUTHORIZED)    
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from core_root_api.security.auth.serializer.login import LoginSerializerClass
from core_root_api.security.user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
        # return Response({"error_message":"Could not login, due to invalid credentials",'status':False}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from core_root_api.security.auth.serializer.login import LoginSerializerClass
from rest_framework import viewsets
from core_root_api.security.user.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from django.http import HttpResponseRedirect
from core_root_api.security import base_url
import datetime
import time
import platform
increment=0
class LoginViewSet(viewsets.ViewSet):
    serializer_class = LoginSerializerClass
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "error": "Invalid data format.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "status": False,
                "error": "No account found with this email address."
            }, status=status.HTTP_404_NOT_FOUND)

        if not user.is_active:
            return Response({
                "status": False,
                "error": "Account is inactive. Please activate your account first."
            }, status=status.HTTP_403_FORBIDDEN)

        # Use authenticate to validate password
        user_auth = authenticate(username=user.email, password=password)

        if user_auth is None:
            return Response({
                "status": False,
                "error": "Incorrect password. Please try again."
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Optional: Generate JWT token manually
        refresh = RefreshToken.for_user(user)

        return Response({
        "status": True,
        "message": "Login successful.",
        "data": {
            "user": {
                "id": str(user.public_id).replace("-", ""),
                "full_name": user.full_name,
                "username": user.username,
                "profile_image": (
                    user.profile_image if isinstance(user.profile_image, str)
                    else user.profile_image.url if user.profile_image else None
                ),
                "email": user.email,
                "is_active": user.is_active,
                "created": user.created,
                "updated": user.updated,
            },
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)



class AdminLoginViewset(viewsets.ModelViewSet):
    serializer_class = LoginSerializerClass
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                valid_user=User.objects.get(email=str(serializer.initial_data['email']))
                if valid_user.is_active==False:
                    return Response({"error_message":"You have to activate your account first","status":False}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"status":True,"data":serializer.validated_data,"message":"Login Successful"}, status=status.HTTP_200_OK)
                    # return HttpResponseRedirect(f"{base_url.main_url}/library/dashboard/")
            else:
                return Response({'error_msg':'User  with that email or password does not exist','status':False},status=status.HTTP_401_UNAUTHORIZED)

        except:
           
            return Response({'error_msg':'User  with that email or password does not exist','status':False},status=status.HTTP_401_UNAUTHORIZED)    

        # return Response({"error_message":"Could not login, due to invalid credentials",'status':False}, status=status.HTTP_400_BAD_REQUEST)
    
# class StoreCurrentUserTokenViewset(viewsets.ModelViewSet):
#     http_method_names=['post']
#     permission_classes=[IsAuthenticated,]
   

    # def create(self,request,*args,**kwargs):
    #     user_email=request.user
    #     current_user=self.serializer_class(data=request.data)
    #     current_user.save()
    #     return Response({"token_update_message":"User token Updated"},status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

class UpdateLastLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Update the last login of the authenticated user
        request.user.last_login = timezone.now()
        request.user.save()
        return Response({"message": "Last login updated."})


# class StoreCurrentUserTokenViewset(viewsets.ModelViewSet):
#     http_method_names=['post']
#     permission_classes=[IsAuthenticated,]
   

    # def create(self,request,*args,**kwargs):
    #     user_email=request.user
    #     current_user=self.serializer_class(data=request.data)
    #     current_user.save()
    #     return Response({"token_update_message":"User token Updated"},status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

class UpdateLastLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Update the last login of the authenticated user
        request.user.last_login = timezone.now()
        request.user.save()
        return Response({"message": "Last login updated."})

