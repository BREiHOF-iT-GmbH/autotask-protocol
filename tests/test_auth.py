from autotask_protocol import build_auth_headers


def test_builds_expected_header_names():
    headers = build_auth_headers(username="api-user", secret="s3cr3t", integration_code="CODE-1")
    assert set(headers) == {"UserName", "Secret", "ApiIntegrationCode"}


def test_unescapes_doubled_dollar_in_secret_and_integration_code():
    headers = build_auth_headers(username="u", secret="a$$b$$c", integration_code="X$$Y")
    assert headers["Secret"] == "a$b$c"
    assert headers["ApiIntegrationCode"] == "X$Y"


def test_username_is_passed_through_unescaped():
    headers = build_auth_headers(username="u$$ser", secret="s", integration_code="c")
    assert headers["UserName"] == "u$$ser"


def test_values_without_escaping_are_unchanged():
    headers = build_auth_headers(username="u", secret="plain", integration_code="plain2")
    assert headers["Secret"] == "plain"
    assert headers["ApiIntegrationCode"] == "plain2"
