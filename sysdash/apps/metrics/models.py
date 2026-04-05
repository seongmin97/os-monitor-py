from django.db import models
from apps.servers.models import Server


class MetricSnapshot(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="metrics")
    cpu_percent = models.FloatField()
    memory_percent = models.FloatField()
    memory_used_mb = models.PositiveIntegerField()
    disk_percent = models.FloatField()
    net_bytes_sent = models.BigIntegerField()
    net_bytes_recv = models.BigIntegerField()
    collected_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-collected_at"]

    def __str__(self):
        return f"{self.server.name} @ {self.collected_at}"
