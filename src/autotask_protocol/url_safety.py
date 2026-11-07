import httpx


class UnsafeUrlError(ValueError):
    """Raised when a computed Autotask URL would escape the configured API origin or path."""


def safe_join_url(base_url: httpx.URL | str, path: str) -> httpx.URL:
    """Joins `path` (a relative path or a server-supplied absolute URL, e.g. a pagination
    `nextPageUrl`) onto `base_url` and rejects the result unless it stays on the same
    scheme/host/port, under the base path, free of embedded credentials, and free of
    '.'/'..' segments or backslashes."""
    base = base_url if isinstance(base_url, httpx.URL) else httpx.URL(base_url)
    url = base.join(path)
    if (
        (url.scheme, url.host, url.port) != (base.scheme, base.host, base.port)
        or not url.path.startswith(base.path)
        or url.username
        or url.password
        or any(segment in {".", ".."} for segment in url.path.split("/"))
        or "\\" in url.path
    ):
        raise UnsafeUrlError(f"URL außerhalb der konfigurierten Autotask-API: {url}")
    return url
