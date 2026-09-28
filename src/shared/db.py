import os
from abc import ABC, abstractmethod

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from settings import DatabaseSettings
from pathlib import Path


class Database(ABC):
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self.setup()

    @abstractmethod
    def setup(self): ...

    def teardown(self) -> None:
        return None

    @abstractmethod
    def execute_sql(self, sql: str) -> None:
        raise NotImplementedError

    def create_tables_from_migrations(self):
        migrations_path = Path(self.settings.migrations_path).parent
        sql_files = sorted(
            [f for f in os.listdir(migrations_path) if f.endswith(".sql")]
        )

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
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    "name TEXT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT now())"
                )
                cur.execute("SELECT name FROM schema_migrations")
                applied = {row[0] for row in cur.fetchall()}

                if not applied:
                    # База, созданная до появления учёта миграций: схема уже есть.
                    cur.execute("SELECT to_regclass('users') IS NOT NULL")
                    if cur.fetchone()[0]:
                        applied = {"db.sql"}
                        cur.execute(
                            "INSERT INTO schema_migrations (name) VALUES (%s)",
                            ("db.sql",),
                        )

                for file_name in sql_files:
                    if file_name in applied:
                        continue
                    content = (migrations_path / file_name).read_text(encoding="utf-8")
                    for stmt in content.split("-- STATEMENT-END"):
                        cleaned_stmt = stmt.strip()
                        if cleaned_stmt:
                            cur.execute(cleaned_stmt)
                    cur.execute(
                        "INSERT INTO schema_migrations (name) VALUES (%s)",
                        (file_name,),
                    )
        finally:
            # Гарантированно закрываем соединение после всех операций
            if conn:
                conn.close()
