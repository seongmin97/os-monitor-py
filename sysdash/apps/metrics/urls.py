from django.urls import path
from .views import MetricCreateView, MetricListView

urlpatterns = [
    path("", MetricCreateView.as_view(), name="metric-create"),
    path("history/", MetricListView.as_view(), name="metric-list"),
]
