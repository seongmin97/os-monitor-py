from django.db import models
from apps.servers.models import Server


class Alert(models.Model):
    METRIC_CHOICES = [
        ("cpu_percent", "CPU Usage (%)"),
        ("memory_percent", "Memory Usage (%)"),
        ("disk_percent", "Disk Usage (%)"),
    ]

    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name="alerts")
    metric = models.CharField(max_length=50, choices=METRIC_CHOICES)
    threshold = models.FloatField(help_text="Trigger alert when metric exceeds this value")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("server", "metric")

    def __str__(self):
        return f"{self.server.name}: {self.metric} > {self.threshold}"


class AlertEvent(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="events")
    metric_value = models.FloatField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-triggered_at"]

    def __str__(self):
        return f"{self.alert} triggered at {self.triggered_at}"
