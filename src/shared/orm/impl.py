# Прямой импорт psycopg2, как вы и просили
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from pony.orm import db_session
from .models import db
from ..db import Database


class PonyDb(Database):
    @db_session
    def setup(self):
        self.bind()
        self.create_tables_from_migrations()
        self.generate_mapping()

    def bind(self):
        db.bind(
            provider="postgres",
            host=self.settings.host,
            port=self.settings.port,
            user=self.settings.user,
            password=self.settings.password.get_secret_value(),
            database=self.settings.name,
            options=f"-c search_path={self.settings.schema}",
        )

    def generate_mapping(self):
        db.generate_mapping(create_tables=False)

    def execute_sql(self, sql: str) -> None:
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
                cur.execute(f"SET search_path TO {self.settings.schema}")
                cur.execute(sql)

        finally:
            if conn:
                conn.close()
