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
                # Устанавливаем схему ОДИН раз для этого соединения
                cur.execute(f"SET search_path TO {self.settings.schema}")

                # Проходим по всем файлам миграций
                for file_name in sql_files:
                    file_path = migrations_path / file_name
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Разделяем файл на команды
                        statements = content.split("-- STATEMENT-END")

                        # Выполняем каждую команду в том же самом курсоре
                        for stmt in statements:
                            cleaned_stmt = stmt.strip()
                            if cleaned_stmt:
                                # ВАЖНО: Мы больше не вызываем self.execute_sql()!
                                cur.execute(cleaned_stmt)
        finally:
            # Гарантированно закрываем соединение после всех операций
            if conn:
                conn.close()
