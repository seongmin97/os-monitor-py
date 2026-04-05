from rest_framework import serializers
from .models import MetricSnapshot


class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = [
            "id",
            "server",
            "cpu_percent",
            "memory_percent",
            "memory_used_mb",
            "disk_percent",
            "net_bytes_sent",
            "net_bytes_recv",
            "collected_at",
        ]
        read_only_fields = ["id", "server", "collected_at"]
