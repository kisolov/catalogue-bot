from settings import DatabaseSettings, JWTSettings, RedisSettings


def test_database_settings_read_env(monkeypatch):
    monkeypatch.setenv("DB_PROVIDER", "postgres")
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_NAME", "n")
    monkeypatch.setenv("DB_SCHEMA", "s")

    settings = DatabaseSettings()

    assert settings.user == "u"
    assert settings.schema == "s"
    assert settings.password.get_secret_value() == "p"
    assert "p" not in repr(settings.password)


def test_redis_settings_defaults():
    settings = RedisSettings()

    assert settings.prefix == "app:"


def test_jwt_settings_default_algorithm(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "k")

    assert JWTSettings().algorithm == "HS256"
