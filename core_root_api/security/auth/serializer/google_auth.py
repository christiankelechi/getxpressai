from rest_framework import serializers

class GoogleAuthSerializer(serializers.Serializer):
    social_user_id=serializers.CharField(write_only=True)
    email=serializers.CharField(write_only=True)
    profile_image=serializers.CharField(write_only=True)
    name=serializers.CharField(write_only=True)