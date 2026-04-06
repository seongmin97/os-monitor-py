from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import MetricSnapshot
from .serializers import MetricSnapshotSerializer
from .authentication import ApiKeyAuthentication


class MetricCreateView(generics.CreateAPIView):
    """Receives metric data from agents authenticated with API key."""

    serializer_class = MetricSnapshotSerializer
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # request.user is the Server instance when authenticated via ApiKeyAuthentication
        serializer.save(server=self.request.user)


class MetricListView(generics.ListAPIView):
    """Returns paginated metric history for a given server. Requires JWT auth."""

    serializer_class = MetricSnapshotSerializer

    def get_queryset(self):
        server_id = self.request.query_params.get("server")
        hours = int(self.request.query_params.get("hours", 24))
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
