import logging

from celery import shared_task
from django.conf import settings
from django.db import connection

log = logging.getLogger(__name__)


@shared_task
def prune_metric_snapshots() -> None:
    """Delete older MetricSnapshot rows globally; keep the newest METRIC_SNAPSHOT_MAX_ROWS."""
    max_rows = getattr(settings, "METRIC_SNAPSHOT_MAX_ROWS", 4000)
    if max_rows < 1:
        return

    sql = """
        DELETE FROM metrics_metricsnapshot
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                    ROW_NUMBER() OVER (
                        ORDER BY collected_at DESC, id DESC
                    ) AS rn
                FROM metrics_metricsnapshot
            ) ranked
            WHERE rn > %s
        )
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [max_rows])
        deleted = cursor.rowcount
    if deleted:
        log.info("Pruned %s metric snapshot(s); cap=%s", deleted, max_rows)
