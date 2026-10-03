import unittest

from app.core.config import get_settings
from app.infrastructure.database.connection import (
    check_database_connection,
    get_connection,
)


class DatabaseConnectionTests(unittest.TestCase):
    def test_database_connection_is_available(self):
        self.assertTrue(
            check_database_connection()
        )

    def test_database_can_execute_query(self):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT 1"
            ).fetchone()

        self.assertEqual(
            row[0],
            1,
        )

    def test_database_configuration_is_loaded_from_environment(self):
        settings = get_settings()

        self.assertTrue(
            bool(settings.database_url_value)
        )

        self.assertTrue(
            bool(settings.secret_key_value)
        )


if __name__ == "__main__":
    unittest.main()