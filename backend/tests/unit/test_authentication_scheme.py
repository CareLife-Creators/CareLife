import unittest

from app.presentation.api.dependencies.authentication import (
    get_bearer_token,
)


class BearerAuthenticationSchemeTests(unittest.TestCase):
    def test_standard_bearer_scheme_is_accepted(self):
        token = get_bearer_token("Bearer test-token")

        self.assertEqual(token, "test-token")

    def test_lowercase_bearer_scheme_is_accepted(self):
        token = get_bearer_token("bearer test-token")

        self.assertEqual(token, "test-token")

    def test_uppercase_bearer_scheme_is_accepted(self):
        token = get_bearer_token("BEARER test-token")

        self.assertEqual(token, "test-token")

    def test_mixed_case_bearer_scheme_is_accepted(self):
        token = get_bearer_token("bEaReR test-token")

        self.assertEqual(token, "test-token")


if __name__ == "__main__":
    unittest.main()