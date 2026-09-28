import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.shared.orm.impl import PonyDb
from src.shared.orm.models import db


class TestPonyDb(PonyDb):
    def teardown(self) -> None:
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.settings.host,
                port=self.settings.port,
                user=self.settings.user,
                password=self.settings.password.get_secret_value(),
                dbname=self.settings.name,
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cur:
                cur.execute(f"DROP SCHEMA IF EXISTS {self.settings.schema} CASCADE;")
                cur.execute(f"CREATE SCHEMA {self.settings.schema};")
        finally:
            if conn:
                conn.close()

        # Disconnect completely
        db.disconnect()
        db.provider = None
        db.schema = None

    def setup(self):
        self.teardown()
        self.create_tables_from_migrations()
        # Ensure database is disconnected before binding
        db.disconnect()
        db.provider = None
        db.schema = None
        self.bind()
        self.generate_mapping()
