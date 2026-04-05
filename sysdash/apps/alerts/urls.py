from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, AlertEventViewSet

router = DefaultRouter()
router.register(r"rules", AlertViewSet, basename="alert")
router.register(r"events", AlertEventViewSet, basename="alert-event")

urlpatterns = [
    path("", include(router.urls)),
]
