from tests.cases.base import BaseTestGroup

MIGRATIONS = ["db.sql", "db_002_products_category_restrict.sql"]


async def _query(db, sql):
    async with db.engine.begin() as conn:
        result = await conn.exec_driver_sql(sql)
        return result.fetchall() if result.returns_rows else None


class TestMigrations(BaseTestGroup):
    async def test_migrations_are_idempotent(self):
        db = self.container.database()

        await db.migrate()

        rows = await _query(db, "SELECT name FROM schema_migrations ORDER BY name")
        assert [r[0] for r in rows] == MIGRATIONS

    async def test_product_category_fk_restricts_delete(self):
        db = self.container.database()

        rows = await _query(
            db,
            "SELECT delete_rule FROM information_schema.referential_constraints "
            "WHERE constraint_name = 'fk_product_category'",
        )

        assert [r[0] for r in rows] == ["RESTRICT"]

    async def test_database_without_migration_log_only_skips_first_migration(self):
        db = self.container.database()
        await _query(db, "DROP TABLE schema_migrations")

        await db.migrate()

        rows = await _query(db, "SELECT name FROM schema_migrations ORDER BY name")
        assert [r[0] for r in rows] == MIGRATIONS
