def build_auth_headers(*, username: str, secret: str, integration_code: str) -> dict[str, str]:
    """Autotask REST API auth headers, including the vendor's '$$' -> '$' escaping quirk
    for Secret and ApiIntegrationCode (values are stored/transmitted with '$' doubled)."""
    return {
        "UserName": username,
        "Secret": secret.replace("$$", "$"),
        "ApiIntegrationCode": integration_code.replace("$$", "$"),
    }
