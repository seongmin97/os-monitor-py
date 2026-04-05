from rest_framework import serializers
from .models import Server


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ["id", "name", "api_key", "description", "is_active", "created_at"]
        read_only_fields = ["id", "api_key", "created_at"]
