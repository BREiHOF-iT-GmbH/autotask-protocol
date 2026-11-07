import httpx
import pytest

from autotask_protocol import UnsafeUrlError, safe_join_url

BASE = "https://webservices18.autotask.net/atservicesrest/v1.0/"


def test_relative_path_joins_cleanly():
    url = safe_join_url(BASE, "Tickets/query")
    assert str(url) == BASE + "Tickets/query"


def test_rejects_different_host():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "https://evil.example.com/Tickets/query")


def test_rejects_different_scheme():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "http://webservices18.autotask.net/atservicesrest/v1.0/Tickets")


def test_rejects_different_port():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "https://webservices18.autotask.net:8443/atservicesrest/v1.0/Tickets")


def test_rejects_path_escaping_base():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "/other/path")


def test_rejects_dot_dot_segment():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "../../etc/passwd")


def test_rejects_embedded_credentials():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "https://user:pass@webservices18.autotask.net/atservicesrest/v1.0/Tickets")


def test_rejects_backslash_in_path():
    with pytest.raises(UnsafeUrlError):
        safe_join_url(BASE, "Tickets\\..\\query")


def test_accepts_httpx_url_as_base():
    url = safe_join_url(httpx.URL(BASE), "Tickets/query")
    assert str(url) == BASE + "Tickets/query"


def test_server_supplied_next_page_url_on_same_origin_is_accepted():
    next_page = BASE + "Tickets/query?page=2"
    url = safe_join_url(BASE, next_page)
    assert str(url) == next_page
