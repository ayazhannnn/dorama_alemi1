"""pytest: DORA скриптінің есептеу логикасы (tools/dora_metrics.py)."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dora_metrics as d  # noqa: E402

NOW = datetime(2026, 11, 10, tzinfo=timezone.utc)
SINCE = NOW - timedelta(days=90)


def h(hours):
    return NOW - timedelta(hours=hours)


def make():
    rel = [{"tag": "v1", "at": h(500)}, {"tag": "v2", "at": h(300)}, {"tag": "v3", "at": h(100)}]
    prs = [
        {"number": 1, "first_commit": h(520), "merged": h(510), "hotfix": False},
        {"number": 2, "first_commit": h(290), "merged": h(280), "hotfix": True},
    ]
    inc = [{"number": 5, "created": h(50), "closed": h(46)}]
    return rel, prs, inc


def test_lead_time_median():
    m = d.compute(*make(), SINCE, NOW)
    assert m["lead_time_h_median"] == 105.0  # (20 + 190) / 2


def test_change_failure_rate():
    m = d.compute(*make(), SINCE, NOW)
    assert m["failed_deployments"] == 1 and m["change_failure_rate_pct"] == 33.3


def test_mttr():
    m = d.compute(*make(), SINCE, NOW)
    assert m["mttr_h_mean"] == 4.0


def test_no_data_is_not_a_crash():
    m = d.compute([], [], [], SINCE, NOW)
    assert m["deployments"] == 0 and m["change_failure_rate_pct"] is None
    assert d.level(m)["mttr"] == "дерек жоқ"


def test_levels():
    m = d.compute(*make(), SINCE, NOW)
    lv = d.level(m)
    assert lv["lead_time"] == "High" and lv["mttr"] == "High"
