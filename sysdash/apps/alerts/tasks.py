import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

log = logging.getLogger(__name__)

COOLDOWN_MINUTES = 5


@shared_task
def check_alerts(snapshot_id: int) -> None:
    """
    Check all active alert rules for the server that produced this snapshot.
    Creates an AlertEvent when a threshold is exceeded, subject to a cooldown
    so the same rule cannot fire more than once every COOLDOWN_MINUTES.
    """
    from apps.metrics.models import MetricSnapshot
    from apps.alerts.models import Alert, AlertEvent

    try:
        snapshot = MetricSnapshot.objects.select_related("server").get(pk=snapshot_id)
    except MetricSnapshot.DoesNotExist:
        log.warning("check_alerts: snapshot %s not found, skipping.", snapshot_id)
        return

    active_rules = Alert.objects.filter(server=snapshot.server, is_active=True)
    if not active_rules.exists():
        return

    cooldown_cutoff = timezone.now() - timedelta(minutes=COOLDOWN_MINUTES)

    for rule in active_rules:
        metric_value = getattr(snapshot, rule.metric, None)
        if metric_value is None:
            continue

        if metric_value <= rule.threshold:
            continue

        # Skip if this rule already fired within the cooldown window
        recent = AlertEvent.objects.filter(
            alert=rule,
            triggered_at__gte=cooldown_cutoff,
        ).exists()
        if recent:
            continue

        AlertEvent.objects.create(alert=rule, metric_value=metric_value)
        log.warning(
            "ALERT — server=%s  rule=%s  %s=%.1f > threshold=%.1f",
            snapshot.server.name,
            rule.pk,
            rule.metric,
            metric_value,
            rule.threshold,
        )
