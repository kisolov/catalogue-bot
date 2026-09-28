import json

import pytest
from pydantic import ValidationError

from settings import JWTSettings, ServerSettings
from src.bootstrap.utils.logging_middleware import mask_body, mask_headers


def test_authorization_header_is_masked():
    masked = mask_headers({"Authorization": "Bearer secret.jwt", "accept": "*/*"})

    assert masked == {"Authorization": "***", "accept": "*/*"}


def test_tokens_and_init_data_are_masked_in_json_body():
    body = json.dumps(
        {"init_data": "hash=abc", "nested": {"access_token": "jwt"}, "ok": 1}
    )

    masked = json.loads(mask_body(body))

    assert masked == {"init_data": "***", "nested": {"access_token": "***"}, "ok": 1}


def test_non_json_body_is_not_logged():
    assert mask_body("user=1&hash=abc") == "<non-json body hidden>"


def test_wildcard_origin_is_rejected(monkeypatch):
    monkeypatch.setenv("SERVER_ALLOWED_ORIGINS", '["*"]')
    monkeypatch.setenv("SERVER_PORT", "8000")
    monkeypatch.setenv("SERVER_HOST", "127.0.0.1")

    with pytest.raises(ValidationError):
        ServerSettings()


def test_wildcard_proxy_is_rejected(monkeypatch):
    monkeypatch.setenv("SERVER_ALLOWED_ORIGINS", '["https://a.example"]')
    monkeypatch.setenv("SERVER_PORT", "8000")
    monkeypatch.setenv("SERVER_HOST", "127.0.0.1")
    monkeypatch.setenv("SERVER_FORWARDED_ALLOW_IPS", "*")

    with pytest.raises(ValidationError):
        ServerSettings()


def test_token_lifetime_is_bounded(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "k")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", str(60 * 24 * 30))

    with pytest.raises(ValidationError):
        JWTSettings()
