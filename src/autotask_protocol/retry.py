import email.utils
from datetime import datetime, timezone

RETRYABLE_STATUS_CODES = frozenset({408, 425, 429, 500, 502, 503, 504})


def parse_retry_after_seconds(value: str | None, *, cap_seconds: float = 60.0) -> float | None:
    """Parses a Retry-After header value (seconds or HTTP-date) into a clamped delay in
    [0, cap_seconds], or None when the value is absent or unparseable."""
    if not value:
        return None
    try:
        return min(cap_seconds, max(0.0, float(value)))
    except ValueError:
        pass
    try:
        retry_at = email.utils.parsedate_to_datetime(value)
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return min(cap_seconds, max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds()))
    except (ValueError, TypeError):
        return None


def compute_backoff_delay(
    attempt: int,
    retry_after_header: str | None,
    *,
    retry_after_cap: float = 60.0,
    backoff_cap: float = 30.0,
) -> float:
    """Delay before the next retry attempt: honors a server-supplied Retry-After header when
    present and parseable, otherwise falls back to exponential backoff (2 * 2**attempt, capped)."""
    parsed = parse_retry_after_seconds(retry_after_header, cap_seconds=retry_after_cap)
    if parsed is not None:
        return parsed
    return min(2 * 2**attempt, backoff_cap)
