from rest_framework import viewsets
from .models import Alert, AlertEvent
from .serializers import AlertSerializer, AlertEventSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().select_related("server")
    serializer_class = AlertSerializer


class AlertEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertEvent.objects.all().select_related("alert__server")
    serializer_class = AlertEventSerializer
