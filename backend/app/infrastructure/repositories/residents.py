from enum import Enum
from uuid import uuid4

from app.domain.entities.resident import (
    ResidentProfile,
    ResidentProfileStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.infrastructure.database.connection import get_connection


_PROFILE_COLUMNS = """
    id,
    organization_id,
    full_name,
    preferred_name,
    date_of_birth,
    room_number,
    emergency_contact_name,
    emergency_contact_phone,
    status,
    created_by,
    updated_by,
    created_at,
    updated_at
"""

_UPDATE_COLUMNS = {
    "full_name": "full_name",
    "preferred_name": "preferred_name",
    "date_of_birth": "date_of_birth",
    "room_number": "room_number",
    "emergency_contact_name": "emergency_contact_name",
    "emergency_contact_phone": "emergency_contact_phone",
    "status": "status",
}


def _to_profile(row) -> ResidentProfile:
    return ResidentProfile(
        id=row[0],
        organization_id=row[1],
        full_name=row[2],
        preferred_name=row[3],
        date_of_birth=row[4],
        room_number=row[5],
        emergency_contact_name=row[6],
        emergency_contact_phone=row[7],
        status=ResidentProfileStatus(row[8]),
        created_by=row[9],
        updated_by=row[10],
        created_at=row[11],
        updated_at=row[12],
    )


class PostgresResidentProfileRepository:

    @staticmethod
    def _assert_care_home_access(
        connection,
        user: UserContext,
        organization_id: str,
    ) -> None:
        organization = connection.execute(
            """
            SELECT 1
            FROM organizations o
            JOIN verification_statuses vs
              ON vs.id = o.status_id
            WHERE o.id = %s
              AND o.organization_type = 'elderly_care'
              AND vs.name = 'verified'
            LIMIT 1
            """,
            (organization_id,),
        ).fetchone()

        if organization is None:
            raise LookupError(
                "Verified elder-care organization not found"
            )

        if user.role == Role.CARELIFE_ADMIN:
            return

        if user.role != Role.CARE_HOME_STAFF:
            raise PermissionError(
                "Care-home staff access is required"
            )

        membership = connection.execute(
            """
            SELECT 1
            FROM user_organizations uo
            JOIN users u
              ON u.id = uo.user_id
            JOIN roles r
              ON r.id = u.role_id
            WHERE uo.organization_id = %s
              AND u.id = %s
              AND u.is_active = TRUE
              AND r.name = 'care_home_staff'
            LIMIT 1
            """,
            (organization_id, user.user_id),
        ).fetchone()

        if membership is None:
            raise PermissionError(
                "You are not authorized for this care home"
            )

    def create_profile(
        self,
        user: UserContext,
        organization_id: str,
        values: dict[str, object],
    ) -> ResidentProfile:
        with get_connection() as connection:
            with connection.transaction():
                self._assert_care_home_access(
                    connection,
                    user,
                    organization_id,
                )

                row = connection.execute(
                    f"""
                    INSERT INTO resident_profiles (
                        id,
                        organization_id,
                        full_name,
                        preferred_name,
                        date_of_birth,
                        room_number,
                        emergency_contact_name,
                        emergency_contact_phone,
                        status,
                        created_by,
                        updated_by,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s,
                        'active', %s, %s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    RETURNING {_PROFILE_COLUMNS}
                    """,
                    (
                        str(uuid4()),
                        organization_id,
                        values["full_name"],
                        values.get("preferred_name"),
                        values.get("date_of_birth"),
                        values.get("room_number"),
                        values.get("emergency_contact_name"),
                        values.get("emergency_contact_phone"),
                        user.user_id,
                        user.user_id,
                    ),
                ).fetchone()

        return _to_profile(row)

    def list_profiles(
        self,
        user: UserContext,
        organization_id: str,
        profile_status: ResidentProfileStatus | None = None,
    ) -> list[ResidentProfile]:
        with get_connection() as connection:
            self._assert_care_home_access(
                connection,
                user,
                organization_id,
            )

            if profile_status is None:
                rows = connection.execute(
                    f"""
                    SELECT {_PROFILE_COLUMNS}
                    FROM resident_profiles
                    WHERE organization_id = %s
                    ORDER BY full_name ASC, id ASC
                    """,
                    (organization_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    f"""
                    SELECT {_PROFILE_COLUMNS}
                    FROM resident_profiles
                    WHERE organization_id = %s
                      AND status = %s
                    ORDER BY full_name ASC, id ASC
                    """,
                    (
                        organization_id,
                        profile_status.value,
                    ),
                ).fetchall()

        return [_to_profile(row) for row in rows]

    def get_profile(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
    ) -> ResidentProfile | None:
        with get_connection() as connection:
            self._assert_care_home_access(
                connection,
                user,
                organization_id,
            )

            row = connection.execute(
                f"""
                SELECT {_PROFILE_COLUMNS}
                FROM resident_profiles
                WHERE id = %s
                  AND organization_id = %s
                LIMIT 1
                """,
                (resident_id, organization_id),
            ).fetchone()

        if row is None:
            return None

        return _to_profile(row)

    def update_profile(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
        changes: dict[str, object],
    ) -> ResidentProfile | None:
        selected = {
            key: value
            for key, value in changes.items()
            if key in _UPDATE_COLUMNS
        }

        if not selected:
            raise ValueError(
                "At least one resident field must be provided"
            )

        assignments = []
        values = []

        for key, value in selected.items():
            assignments.append(f"{_UPDATE_COLUMNS[key]} = %s")

            if isinstance(value, Enum):
                value = value.value

            values.append(value)

        with get_connection() as connection:
            with connection.transaction():
                self._assert_care_home_access(
                    connection,
                    user,
                    organization_id,
                )

                current_row = connection.execute(
                    f"""
                    SELECT {_PROFILE_COLUMNS}
                    FROM resident_profiles
                    WHERE id = %s
                      AND organization_id = %s
                    FOR UPDATE
                    """,
                    (resident_id, organization_id),
                ).fetchone()

                if current_row is None:
                    return None

                current_contact_name = current_row[6]
                current_contact_phone = current_row[7]

                new_contact_name = selected.get(
                    "emergency_contact_name",
                    current_contact_name,
                )

                new_contact_phone = selected.get(
                    "emergency_contact_phone",
                    current_contact_phone,
                )

                if (
                    (new_contact_name is None)
                    != (new_contact_phone is None)
                ):
                    raise ValueError(
                        "Emergency contact name and phone must be "
                        "provided together"
                    )

                assignments.extend(
                    [
                        "updated_by = %s",
                        "updated_at = CURRENT_TIMESTAMP",
                    ]
                )

                values.extend(
                    [
                        user.user_id,
                        resident_id,
                        organization_id,
                    ]
                )

                updated_row = connection.execute(
                    f"""
                    UPDATE resident_profiles
                    SET {", ".join(assignments)}
                    WHERE id = %s
                      AND organization_id = %s
                    RETURNING {_PROFILE_COLUMNS}
                    """,
                    values,
                ).fetchone()

        if updated_row is None:
            return None

        return _to_profile(updated_row)