from django.contrib import admin
from .models import Alert, AlertEvent


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["server", "metric", "threshold", "is_active", "created_at"]
    list_filter = ["is_active", "metric"]
    search_fields = ["server__name"]


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ["alert", "metric_value", "triggered_at", "resolved_at"]
    list_filter = ["alert__metric"]
    readonly_fields = ["alert", "metric_value", "triggered_at"]
    ordering = ["-triggered_at"]
