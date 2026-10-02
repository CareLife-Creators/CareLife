from collections.abc import Iterator
from contextlib import contextmanager

import psycopg

from app.core.config import get_settings


def _get_database_url() -> str:
    url = get_settings().database_url_value

    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url[len("postgresql+psycopg://"):]

    return url


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    connection = psycopg.connect(_get_database_url())

    try:
        yield connection
    finally:
        connection.close()


def check_database_connection() -> bool:
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1").fetchone()

        return True
    except psycopg.Error:
        return False