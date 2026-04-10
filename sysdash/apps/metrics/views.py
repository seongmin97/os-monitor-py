import logging

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import MetricSnapshot
from .serializers import MetricSnapshotSerializer
from .authentication import ApiKeyAuthentication

_channel_layer = get_channel_layer()
log = logging.getLogger(__name__)


class MetricCreateView(generics.CreateAPIView):
    """Receives metric data from agents authenticated with API key."""

    serializer_class = MetricSnapshotSerializer
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        snapshot = serializer.save(server=self.request.user)
        group_name = f"server_{snapshot.server_id}"
        payload = {"type": "metric.update", "data": MetricSnapshotSerializer(snapshot).data}

        # Broadcast to all WebSocket clients subscribed to this server
        log.info(
            "Publishing to Redis channel layer: group=%s payload=%s",
            group_name,
            payload,
        )
        log.info(
            "Publishing metric snapshot %s to Redis channel layer group server_%s",
            snapshot.id,
            snapshot.server_id,
        )
        async_to_sync(_channel_layer.group_send)(
            group_name,
            payload,
        )

        # Async alert evaluation — runs in Celery worker, does not block the response
        from apps.alerts.tasks import check_alerts
        check_alerts.delay(snapshot.id)


class MetricListView(generics.ListAPIView):
    """Returns paginated metric history for a given server. Requires JWT auth."""

    serializer_class = MetricSnapshotSerializer

    def get_queryset(self):
        server_id = self.request.query_params.get("server")
        try:
            hours = max(1, int(self.request.query_params.get("hours", 24)))
        except (ValueError, TypeError):
            hours = 24
        since = timezone.now() - timedelta(hours=hours)

        qs = MetricSnapshot.objects.filter(collected_at__gte=since).order_by("collected_at")
        if server_id:
            qs = qs.filter(server_id=server_id)
        return qs


class MetricLatestView(generics.RetrieveAPIView):
    """Returns the single most recent snapshot for a server. Requires JWT auth."""

    serializer_class = MetricSnapshotSerializer

    def get_object(self):
        server_id = self.request.query_params.get("server")
        qs = MetricSnapshot.objects.all()
        if server_id:
            qs = qs.filter(server_id=server_id)
        snapshot = qs.first()
        if snapshot is None:
            from rest_framework.exceptions import NotFound
            raise NotFound("No metrics found for this server.")
        return snapshot
