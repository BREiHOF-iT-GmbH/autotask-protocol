# autotask-protocol

Shared, transport-agnostic Autotask REST API protocol logic used by
[SupportDesk](https://github.com/BREiHOF-iT-GmbH/SupportDesk) and
[autotask_RE](https://github.com/dietmarbreihof-beep/servicedesk).

This package deliberately ships **no HTTP client**: SupportDesk calls Autotask
asynchronously (`httpx.AsyncClient`), autotask_RE calls it synchronously
(`httpx.Client`). Forcing one shared transport client would mean rewriting one
of the two apps' concurrency models, which neither app asked for. Instead,
each app keeps its own client and wires these pure functions into it.

## What's here

- `build_auth_headers(...)` — the `UserName`/`Secret`/`ApiIntegrationCode`
  headers, including Autotask's `$$` → `$` escaping quirk for `Secret` and
  `ApiIntegrationCode`.
- `RETRYABLE_STATUS_CODES`, `compute_backoff_delay(...)`,
  `parse_retry_after_seconds(...)` — which HTTP statuses are safe to retry,
  and how long to wait (honoring a server `Retry-After` header — seconds or
  HTTP-date — falling back to capped exponential backoff).
- `safe_join_url(...)` — joins a relative path or a server-supplied absolute
  URL (e.g. a pagination `nextPageUrl`) onto the configured API base and
  rejects anything that would escape its scheme/host/port/path, embed
  credentials, or contain `.`/`..`/backslash path segments.
- `ThresholdPolicy` — a pure function translating Autotask's own documented
  hour-quota warning thresholds (extra vendor-side latency at 50 %/75 % of
  the rolling 60-minute call budget) into a client-side proactive delay, fed
  from the vendor's own `ThresholdInformation` endpoint.

## Why this exists

SupportDesk and autotask_RE each implemented their own Autotask HTTP client
independently, with identical credential-escaping logic duplicated across
both repos, and no coordination for Autotask's shared, tenant-wide hourly
call quota (10,000 calls/60 minutes, shared across all integrations under
one Autotask database — see SupportDesk's
`docs/autotask-parallelitaet.md`). This package is the single place that
knowledge now lives, so both apps draw on one Retry-After parser, one URL
safety check, and one hour-quota policy instead of two independently
maintained (and already slightly inconsistent) copies.

## Install

```
pip install git+https://github.com/BREiHOF-iT-GmbH/autotask-protocol.git@main
```

## Develop

```
pip install -e ".[dev]"
pytest
```
