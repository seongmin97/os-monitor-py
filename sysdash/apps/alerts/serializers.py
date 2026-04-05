from rest_framework import serializers
from .models import Alert, AlertEvent


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["id", "server", "metric", "threshold", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class AlertEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertEvent
        fields = ["id", "alert", "metric_value", "triggered_at", "resolved_at"]
        read_only_fields = ["id", "triggered_at"]
