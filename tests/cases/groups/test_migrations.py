import psycopg2

from settings import DatabaseSettings
from tests.cases.base import BaseTestGroup
from tests.utils.test_db import TestPonyDb

MIGRATIONS = ["db.sql", "db_002_products_category_restrict.sql"]


def _query(settings, sql):
    conn = psycopg2.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password.get_secret_value(),
        dbname=settings.name,
    )
    try:
        with conn, conn.cursor() as cur:
            cur.execute(f"SET search_path TO {settings.schema}")
            cur.execute(sql)
            return cur.fetchall() if cur.description else None
    finally:
        conn.close()


class TestMigrations(BaseTestGroup):
    def test_migrations_are_idempotent(self):
        settings = DatabaseSettings()
        db = TestPonyDb(settings)

        db.create_tables_from_migrations()

        rows = _query(settings, "SELECT name FROM schema_migrations ORDER BY name")
        assert [r[0] for r in rows] == MIGRATIONS

    def test_product_category_fk_restricts_delete(self):
        settings = DatabaseSettings()

        rows = _query(
            settings,
            "SELECT delete_rule FROM information_schema.referential_constraints "
            "WHERE constraint_name = 'fk_product_category'",
        )

        assert [r[0] for r in rows] == ["RESTRICT"]

    def test_database_without_migration_log_only_skips_first_migration(self):
        settings = DatabaseSettings()
        db = TestPonyDb(settings)
        _query(settings, "DROP TABLE schema_migrations")

        db.create_tables_from_migrations()

        rows = _query(settings, "SELECT name FROM schema_migrations ORDER BY name")
        assert [r[0] for r in rows] == MIGRATIONS
