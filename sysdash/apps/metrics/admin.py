from django.contrib import admin
from .models import MetricSnapshot


@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ["server", "cpu_percent", "memory_percent", "disk_percent", "collected_at"]
    list_filter = ["server"]
    readonly_fields = ["server", "cpu_percent", "memory_percent", "memory_used_mb",
                       "disk_percent", "net_bytes_sent", "net_bytes_recv", "collected_at"]
    ordering = ["-collected_at"]
