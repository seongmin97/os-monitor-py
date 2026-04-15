from rest_framework import viewsets
from .models import Alert, AlertEvent
from .pagination import AlertEventPagination
from .serializers import AlertSerializer, AlertEventSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().select_related("server")
    serializer_class = AlertSerializer


class AlertEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertEvent.objects.all().select_related("alert__server").order_by(
        "-triggered_at"
    )
    serializer_class = AlertEventSerializer
    pagination_class = AlertEventPagination
