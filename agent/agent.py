#!/usr/bin/env python3
"""
SysDash Agent — runs inside the monitored Linux container.
Collects system metrics every INTERVAL seconds and POSTs to the Django API.
"""
import os
import time
import logging
import requests
import psutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

API_URL = os.environ.get("DJANGO_URL", "http://django:8000")
API_KEY = os.environ.get("SERVER_API_KEY", "")
INTERVAL = int(os.environ.get("COLLECT_INTERVAL", "30"))


def collect_metrics() -> dict:
    net = psutil.net_io_counters()
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": mem.percent,
        "memory_used_mb": mem.used // (1024 * 1024),
        "disk_percent": psutil.disk_usage("/").percent,
        "net_bytes_sent": net.bytes_sent,
        "net_bytes_recv": net.bytes_recv,
    }


def send_metrics(data: dict) -> None:
    url = f"{API_URL}/api/metrics/"
    try:
        resp = requests.post(
            url,
            json=data,
            headers={"X-API-Key": API_KEY},
            timeout=5,
        )
        resp.raise_for_status()
        log.info("Metrics sent: CPU=%.1f%% MEM=%.1f%%", data["cpu_percent"], data["memory_percent"])
    except requests.RequestException as e:
        log.warning("Failed to send metrics: %s", e)


def main():
    log.info("SysDash Agent starting. API=%s  interval=%ds", API_URL, INTERVAL)
    if not API_KEY:
        log.error("SERVER_API_KEY is not set. Exiting.")
        raise SystemExit(1)

    while True:
        metrics = collect_metrics()
        send_metrics(metrics)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
