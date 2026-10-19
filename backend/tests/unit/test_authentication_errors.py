import unittest

from fastapi import HTTPException

from app.presentation.api.dependencies.authentication import (
    get_bearer_token,
)


class BearerAuthenticationErrorTests(unittest.TestCase):
    def test_missing_authorization_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_bearer_token(None)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(
            context.exception.detail,
            "Authentication required",
        )

    def test_empty_authorization_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_bearer_token("")

        self.assertEqual(context.exception.status_code, 401)

    def test_unsupported_authentication_scheme_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_bearer_token("Basic test-token")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(
            context.exception.detail,
            "Invalid authentication scheme",
        )

    def test_bearer_scheme_without_token_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_bearer_token("Bearer    ")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(
            context.exception.detail,
            "Authentication required",
        )

    def test_scheme_without_separator_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_bearer_token("Bearer")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(
            context.exception.detail,
            "Invalid authentication scheme",
        )


if __name__ == "__main__":
    unittest.main()