from core_root_api.security.auth.serializer.confirm_reset_code import ConfirmResetCodeSerializer
from core_root_api.security.auth.models import CodeGenerator
from core_root_api.security.auth.viewsets.password import PasswordManager
from core_root_api.security.user.models import User
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg import openapi

class ChangePassword(viewsets.ModelViewSet):
    
    serializer_class = ConfirmResetCodeSerializer
    permission_classes=[AllowAny,]
    queryset=CodeGenerator.objects.all()
    http_method_names=['post']
    
   
    @swagger_auto_schema(operation_description="Reset Password",)
    def create(self,request):
        serializer=self.serializer_class(data=request.data)
        email = serializer.initial_data.get('email')
        print(email)
        if not email:
            return Response(
                {"is_active": False, "status": False, "error": "No email query"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"status": False, "active": False, "error": f"{email} does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if serializer.is_valid(raise_exception=True):
                code_authentication=serializer.validated_data['code_authentication']
                try:
                    email  = serializer.validated_data.get("email")
            
                    password = serializer.validated_data['password']
                    confirm_password = serializer.validated_data['confirm_password']

                    if password==confirm_password:
                        password_manager = PasswordManager(password).verify_password()
                        if  not password_manager[0]:
                            response_data=dict()
                            # response_data = {"status": False, "error": password_manager[1].split("-")[0].replace("Issues:", "")}
                            issues = password_manager[1].split("-")[1:]
                            response_data['error'] = [value for value in issues]
                            return Response( response_data, status=status.HTTP_400_BAD_REQUEST)
                        if len(password)>=8:
                            try:
                                current_user=User.objects.get(email=email)
                            except User.DoesNotExist:
                                return Response({"status":False,"error":"Password must be at least 8 characters"},status=status.HTTP_400_BAD_REQUEST)
                            current_user.set_password(password)
                        
                            current_user.save()
                            current_user=CodeGenerator.objects.get(code_authentication=code_authentication, user=user)
                            current_user.code_authentication=""
                            current_user.save()
                            return Response({"message": "Password Changed","status":True}, status=status.HTTP_200_OK)
                        else:
                            
                            return Response({"error": "password must be upto 8 characters","status":False}, status=status.HTTP_406_NOT_ACCEPTABLE)

                    else:
                        return Response({"error": "Password and confirm password is not the same","status":False}, status=status.HTTP_400_BAD_REQUEST)

                    
                    # return Response({"status":True,"message":f" successfully confirmed the code for {email}"},status=status.HTTP_200_OK)
                except CodeGenerator.DoesNotExist:
                    return Response({"status":False,"error":"The code provided does not exist"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"status":False,"error":f"Your request cant be processed now, check your network and try again. E: {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    