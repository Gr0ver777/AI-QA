"""Базовый класс для работы с базой данных PostgreSQL."""

import psycopg2
from psycopg2 import sql, extras
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from config import settings


class BaseDatabase:
    """Базовый класс для работы с PostgreSQL."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.host = host or settings.DB_HOST
        self.port = port or settings.DB_PORT
        self.database = database or settings.DB_NAME
        self.user = user or settings.DB_USER
        self.password = password or settings.DB_PASSWORD
        self._connection = None

    @property
    def dsn(self) -> str:
        """Получение DSN строки подключения."""
        return f"host={self.host} port={self.port} dbname={self.database} user={self.user} password={self.password}"

    def connect(self):
        """Подключение к базе данных."""
        if not self._connection or self._connection.closed:
            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
        return self._connection

    def close(self):
        """Закрытие подключения."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    @contextmanager
    def cursor(self, cursor_factory=None):
        """Контекстный менеджер для курсора."""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        """Контекстный менеджер для транзакции."""
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None,
        fetch: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """Выполнение SQL запроса."""
        with self.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                columns = [desc[0] for desc in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            return None

    def execute_many(
        self,
        query: str,
        params_list: List[Tuple[Any, ...]],
    ):
        """Выполнение массового SQL запроса."""
        with self.transaction() as conn:
            with self.cursor() as cursor:
                extras.execute_batch(cursor, query, params_list)

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Вставка записи в таблицу. Возвращает ID новой записи."""
        columns = sql.SQL(", ").join([sql.Identifier(col) for col in data.keys()])
        placeholders = sql.SQL(", ").join([sql.Placeholder()] * len(data))
        query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id").format(
            table=sql.Identifier(table),
            columns=columns,
            placeholders=placeholders,
        )
        with self.cursor() as cursor:
            cursor.execute(query, list(data.values()))
            result = cursor.fetchone()
            return result[0] if result else None

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Tuple[Any, ...],
    ) -> int:
        """Обновление записей в таблице. Возвращает количество обновленных записей."""
        set_clause = sql.SQL(", ").join(
            [sql.SQL("{col} = %s").format(col=sql.Identifier(col)) for col in data.keys()]
        )
        query = sql.SQL("UPDATE {table} SET {set_clause} WHERE {where}").format(
            table=sql.Identifier(table),
            set_clause=set_clause,
            where=sql.SQL(where),
        )
        with self.cursor() as cursor:
            cursor.execute(query, (*list(data.values()), *where_params))
            return cursor.rowcount

    def delete(
        self,
        table: str,
        where: str,
        where_params: Tuple[Any, ...],
    ) -> int:
        """Удаление записей из таблицы. Возвращает количество удаленных записей."""
        query = sql.SQL("DELETE FROM {table} WHERE {where}").format(
            table=sql.Identifier(table),
            where=sql.SQL(where),
        )
        with self.cursor() as cursor:
            cursor.execute(query, where_params)
            return cursor.rowcount

    def select(
        self,
        table: str,
        columns: Optional[List[str]] = None,
        where: Optional[str] = None,
        where_params: Optional[Tuple[Any, ...]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Выборка записей из таблицы."""
        if columns:
            cols = sql.SQL(", ").join([sql.Identifier(col) for col in columns])
        else:
            cols = sql.SQL("*")

        query = sql.SQL("SELECT {cols} FROM {table}").format(
            cols=cols,
            table=sql.Identifier(table),
        )

        if where:
            query += sql.SQL(" WHERE {where}").format(where=sql.SQL(where))

        if order_by:
            query += sql.SQL(" ORDER BY {order}").format(order=sql.SQL(order_by))

        if limit:
            query += sql.SQL(" LIMIT {limit}").format(limit=sql.Literal(limit))

        if offset:
            query += sql.SQL(" OFFSET {offset}").format(offset=sql.Literal(offset))

        return self.execute_query(str(query), where_params)

    def count(self, table: str, where: Optional[str] = None, where_params: Optional[Tuple[Any, ...]] = None) -> int:
        """Подсчет количества записей в таблице."""
        query = sql.SQL("SELECT COUNT(*) FROM {table}").format(table=sql.Identifier(table))
        if where:
            query += sql.SQL(" WHERE {where}").format(where=sql.SQL(where))

        result = self.execute_query(str(query), where_params)
        return result[0]["count"] if result else 0

    def table_exists(self, table_name: str) -> bool:
        """Проверка существования таблицы."""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """
        result = self.execute_query(query, (table_name,))
        return result[0]["exists"] if result else False

    def truncate_table(self, table_name: str):
        """Очистка таблицы."""
        query = sql.SQL("TRUNCATE TABLE {table} RESTART IDENTITY CASCADE").format(
            table=sql.Identifier(table_name)
        )
        with self.transaction():
            with self.cursor() as cursor:
                cursor.execute(str(query))

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
