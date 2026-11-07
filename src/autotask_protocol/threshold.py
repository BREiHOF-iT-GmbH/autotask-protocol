from dataclasses import dataclass


@dataclass(frozen=True)
class ThresholdPolicy:
    """Proactive client-side pacing as the vendor-reported Autotask hour-quota usage climbs.

    Mirrors Autotask's own documented behaviour (extra server-side latency once a tenant's
    rolling 60-minute call budget crosses 50%/75%) so a client can back off before the vendor
    does it for them, using the real `ThresholdInformation` numbers reported by the API."""

    warn_ratio: float = 0.5
    warn_delay_seconds: float = 0.5
    critical_ratio: float = 0.75
    critical_delay_seconds: float = 1.0

    def extra_delay_seconds(self, *, limit: int, used: int) -> float:
        if limit <= 0:
            return 0.0
        ratio = used / limit
        if ratio >= self.critical_ratio:
            return self.critical_delay_seconds
        if ratio >= self.warn_ratio:
            return self.warn_delay_seconds
        return 0.0
