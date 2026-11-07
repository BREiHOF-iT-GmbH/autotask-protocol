import pytest

from autotask_protocol import ThresholdPolicy


@pytest.mark.parametrize(
    "used_ratio,expected_delay",
    [
        (0.0, 0.0),
        (0.49, 0.0),
        (0.50, 0.5),
        (0.60, 0.5),
        (0.74, 0.5),
        (0.75, 1.0),
        (0.99, 1.0),
        (1.00, 1.0),
    ],
)
def test_extra_delay_seconds_follows_vendor_documented_thresholds(used_ratio, expected_delay):
    policy = ThresholdPolicy()
    limit = 10_000
    used = round(limit * used_ratio)
    assert policy.extra_delay_seconds(limit=limit, used=used) == expected_delay


def test_zero_limit_is_treated_as_no_information_available():
    policy = ThresholdPolicy()
    assert policy.extra_delay_seconds(limit=0, used=0) == 0.0


def test_custom_policy_thresholds():
    policy = ThresholdPolicy(warn_ratio=0.3, warn_delay_seconds=1.0, critical_ratio=0.6, critical_delay_seconds=2.0)
    assert policy.extra_delay_seconds(limit=100, used=20) == 0.0
    assert policy.extra_delay_seconds(limit=100, used=30) == 1.0
    assert policy.extra_delay_seconds(limit=100, used=60) == 2.0
