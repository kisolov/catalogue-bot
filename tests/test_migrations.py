import psycopg2

from settings import DatabaseSettings
from tests.utils.test_db import TestPonyDb


def test_migrations_are_idempotent():
    settings = DatabaseSettings()
    db = TestPonyDb(settings)

    db.create_tables_from_migrations()

    conn = psycopg2.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password.get_secret_value(),
        dbname=settings.name,
    )
    with conn, conn.cursor() as cur:
        cur.execute(f"SET search_path TO {settings.schema}")
        cur.execute("SELECT name FROM schema_migrations")
        assert [r[0] for r in cur.fetchall()] == ["db.sql"]
    conn.close()
