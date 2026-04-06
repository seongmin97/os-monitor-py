import psutil
from agent import collect_metrics


def test_cpu_percent():
    cpu_percent = psutil.cpu_percent(interval=1)
    print("cpu_percent:", cpu_percent)
    assert 0 < cpu_percent < 100


def test_all():
    net = psutil.net_io_counters()
    mem = psutil.virtual_memory()
    print(
        "cpu_percent:", psutil.cpu_percent(interval=1),
        "\nphysical_cpu_count:", psutil.cpu_count(logical=False),
        "\nlogical_cpu_count:", psutil.cpu_count(logical=True),
        "\nmemory_percent:", mem.percent,
        "\nmemory_total_mb:", mem.total // (1024 * 1024),
        "\nmemory_used_mb:", mem.used // (1024 * 1024),
        "\ndisk_percent:", psutil.disk_usage("/").percent,
        "\ndisk_total_mb:", psutil.disk_usage("/").total // (1024 * 1024),
        "\ndisk_used_mb:", psutil.disk_usage("/").used // (1024 * 1024),
        "\nnet_bytes_sent:", net.bytes_sent,
        "\nnet_bytes_recv:", net.bytes_recv,
    )


def test_collect_metrics():
    metrics = collect_metrics()
    print("metrics:", metrics)
    assert 0 < metrics["cpu_percent"] < 100
    assert 0 < metrics["memory_percent"] < 100
    assert metrics["memory_used_mb"] > 0
    assert 0 < metrics["disk_percent"] < 100
