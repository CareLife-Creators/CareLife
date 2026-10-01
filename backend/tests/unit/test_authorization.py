import unittest

from fastapi import HTTPException

from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
    require_organization_access,
    require_role,
)


class AuthorizationTests(unittest.TestCase):
    def test_user_with_wrong_role_is_rejected(self):
        user = UserContext(
            user_id="user-1",
            role=Role.PARENT_GUARDIAN,
        )

        check_role = require_role(Role.CARELIFE_ADMIN)

        with self.assertRaises(HTTPException) as context:
            check_role(current_user=user)

        self.assertEqual(context.exception.status_code, 403)

    def test_user_with_required_role_is_allowed(self):
        user = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
        )

        check_role = require_role(Role.CARELIFE_ADMIN)

        result = check_role(current_user=user)

        self.assertEqual(result, user)

    def test_user_from_wrong_organization_is_rejected(self):
        user = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
        )

        with self.assertRaises(HTTPException) as context:
            require_organization_access(
                organization_id="daycare-2",
                current_user=user,
            )

        self.assertEqual(context.exception.status_code, 403)

    def test_user_from_same_organization_is_allowed(self):
        user = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
        )

        result = require_organization_access(
            organization_id="daycare-1",
            current_user=user,
        )

        self.assertEqual(result, user)

    def test_missing_authenticated_user_is_rejected(self):
        from starlette.requests import Request

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
        }

        request = Request(scope)

        with self.assertRaises(HTTPException) as context:
            get_current_user(request)

        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()