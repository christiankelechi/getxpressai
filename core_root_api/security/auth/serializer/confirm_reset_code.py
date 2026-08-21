from rest_framework import serializers
from core_root_api.security.auth.models import CodeGenerator


class ConfirmResetCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password=serializers.CharField()
    confirm_password=serializers.CharField()
    class Meta:
        model=CodeGenerator
        fields=['code_authentication', 'email','password','confirm_password']
    