"""Smoke test to verify test infrastructure works."""


def test_app_imports():
    """Verify core modules can be imported."""
    from app.config import Settings

    s = Settings()
    assert s.dapr_http_port == 3500
