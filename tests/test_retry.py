import email.utils
from datetime import datetime, timedelta, timezone

import pytest

from autotask_protocol import RETRYABLE_STATUS_CODES, compute_backoff_delay, parse_retry_after_seconds


def test_retryable_status_codes_is_the_union_of_both_apps_sets():
    assert RETRYABLE_STATUS_CODES == {408, 425, 429, 500, 502, 503, 504}


def test_parse_retry_after_seconds_numeric():
    assert parse_retry_after_seconds("5") == 5.0


def test_parse_retry_after_seconds_clamped_to_cap():
    assert parse_retry_after_seconds("999", cap_seconds=60.0) == 60.0


def test_parse_retry_after_seconds_negative_clamped_to_zero():
    assert parse_retry_after_seconds("-5") == 0.0


def test_parse_retry_after_seconds_http_date():
    future = datetime.now(timezone.utc) + timedelta(seconds=10)
    header = email.utils.format_datetime(future, usegmt=True)
    result = parse_retry_after_seconds(header, cap_seconds=60.0)
    assert result is not None
    assert 8.0 <= result <= 10.5


def test_parse_retry_after_seconds_absent_is_none():
    assert parse_retry_after_seconds(None) is None
    assert parse_retry_after_seconds("") is None


def test_parse_retry_after_seconds_garbage_is_none():
    assert parse_retry_after_seconds("not-a-date-or-number") is None


@pytest.mark.parametrize("attempt,expected", [(0, 2.0), (1, 4.0), (2, 8.0), (3, 16.0)])
def test_compute_backoff_delay_exponential_without_header(attempt, expected):
    assert compute_backoff_delay(attempt, None, backoff_cap=30.0) == expected


def test_compute_backoff_delay_exponential_caps_out():
    assert compute_backoff_delay(10, None, backoff_cap=30.0) == 30.0


def test_compute_backoff_delay_prefers_retry_after_header():
    assert compute_backoff_delay(0, "7", retry_after_cap=60.0) == 7.0


def test_compute_backoff_delay_falls_back_on_unparseable_header():
    assert compute_backoff_delay(0, "garbage", backoff_cap=30.0) == 2.0
