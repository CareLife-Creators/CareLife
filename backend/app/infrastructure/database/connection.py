from contextlib import contextmanager
from collections.abc import Iterator

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