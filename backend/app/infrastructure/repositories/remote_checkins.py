from uuid import uuid4

from app.domain.entities.remote_checkin import (
    RemoteCheckIn,
    ResidentConsent,
    ResidentConsentStatus,
    WellbeingStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.infrastructure.database.connection import get_connection


_CONSENT_COLUMNS = """
    id,
    resident_id,
    organization_id,
    family_representative_id,
    status,
    granted_by,
    granted_at,
    revoked_by,
    revoked_at,
    created_at,
    updated_at
"""

_CHECKIN_COLUMNS = """
    id,
    consent_id,
    resident_id,
    organization_id,
    actor_user_id,
    wellbeing_status,
    notes,
    recorded_at
"""

_QUALIFIED_CHECKIN_COLUMNS = """
    c.id,
    c.consent_id,
    c.resident_id,
    c.organization_id,
    c.actor_user_id,
    c.wellbeing_status,
    c.notes,
    c.recorded_at
"""


def _to_consent(row) -> ResidentConsent:
    return ResidentConsent(
        id=row[0],
        resident_id=row[1],
        organization_id=row[2],
        family_representative_id=row[3],
        status=ResidentConsentStatus(row[4]),
        granted_by=row[5],
        granted_at=row[6],
        revoked_by=row[7],
        revoked_at=row[8],
        created_at=row[9],
        updated_at=row[10],
    )


def _to_checkin(row) -> RemoteCheckIn:
    return RemoteCheckIn(
        id=row[0],
        consent_id=row[1],
        resident_id=row[2],
        organization_id=row[3],
        actor_user_id=row[4],
        wellbeing_status=WellbeingStatus(row[5]),
        notes=row[6],
        recorded_at=row[7],
    )


class PostgresRemoteCheckInRepository:

    @staticmethod
    def _assert_care_home_access(
        connection,
        organization_id: str,
        user_id: str,
    ) -> None:
        row = connection.execute(
            """
            SELECT 1
            FROM organizations o
            JOIN verification_statuses vs
              ON vs.id = o.status_id
            JOIN user_organizations uo
              ON uo.organization_id = o.id
            JOIN users u
              ON u.id = uo.user_id
            JOIN roles r
              ON r.id = u.role_id
            WHERE o.id = %s
              AND o.organization_type = 'elderly_care'
              AND vs.name = 'verified'
              AND u.id = %s
              AND u.is_active = TRUE
              AND r.name = 'care_home_staff'
            LIMIT 1
            """,
            (organization_id, user_id),
        ).fetchone()

        if row is None:
            raise PermissionError(
                "You are not authorized for this care home"
            )

    def set_consent(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
        family_representative_id: str,
        consent_granted: bool,
    ) -> ResidentConsent:
        status_value = (
            "active" if consent_granted else "revoked"
        )

        with get_connection() as connection:
            with connection.transaction():
                eligible_care_home = connection.execute(
                    """
                    SELECT 1
                    FROM organizations o
                    JOIN verification_statuses vs
                      ON vs.id = o.status_id
                    WHERE o.id = %s
                      AND o.organization_type = 'elderly_care'
                      AND vs.name = 'verified'
                    """,
                    (organization_id,),
                ).fetchone()

                if eligible_care_home is None:
                    raise LookupError(
                        "Verified elderly-care organization not found"
                    )

                if user.role == Role.CARE_HOME_STAFF:
                    self._assert_care_home_access(
                        connection,
                        organization_id,
                        user.user_id,
                    )

                representative = connection.execute(
                    """
                    SELECT 1
                    FROM users u
                    JOIN roles r ON r.id = u.role_id
                    WHERE u.id = %s
                      AND u.is_active = TRUE
                      AND r.name = 'family_representative'
                    """,
                    (family_representative_id,),
                ).fetchone()

                if representative is None:
                    raise LookupError(
                        "Active family representative not found"
                    )

                row = connection.execute(
                    f"""
                    INSERT INTO resident_family_consents (
                        id,
                        resident_id,
                        organization_id,
                        family_representative_id,
                        status,
                        granted_by,
                        granted_at,
                        revoked_by,
                        revoked_at,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        CASE WHEN %s = 'active' THEN %s ELSE NULL END,
                        CASE WHEN %s = 'active'
                             THEN CURRENT_TIMESTAMP ELSE NULL END,
                        CASE WHEN %s = 'revoked' THEN %s ELSE NULL END,
                        CASE WHEN %s = 'revoked'
                             THEN CURRENT_TIMESTAMP ELSE NULL END,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (
                        resident_id,
                        organization_id,
                        family_representative_id
                    )
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        granted_by = CASE
                            WHEN EXCLUDED.status = 'active'
                            THEN EXCLUDED.granted_by
                            ELSE resident_family_consents.granted_by
                        END,
                        granted_at = CASE
                            WHEN EXCLUDED.status = 'active'
                            THEN CURRENT_TIMESTAMP
                            ELSE resident_family_consents.granted_at
                        END,
                        revoked_by = CASE
                            WHEN EXCLUDED.status = 'revoked'
                            THEN EXCLUDED.revoked_by
                            ELSE NULL
                        END,
                        revoked_at = CASE
                            WHEN EXCLUDED.status = 'revoked'
                            THEN CURRENT_TIMESTAMP
                            ELSE NULL
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING {_CONSENT_COLUMNS}
                    """,
                    (
                        str(uuid4()),
                        resident_id,
                        organization_id,
                        family_representative_id,
                        status_value,
                        status_value,
                        user.user_id,
                        status_value,
                        status_value,
                        user.user_id,
                        status_value,
                    ),
                ).fetchone()

        return _to_consent(row)

    def create_checkin(
        self,
        actor_user_id: str,
        resident_id: str,
        wellbeing_status: str,
        notes: str | None,
    ) -> RemoteCheckIn:
        with get_connection() as connection:
            with connection.transaction():

                # Lock the consent record while recording the check-in.
                # This prevents a concurrent consent revocation from
                # racing with check-in creation.
                consent = connection.execute(
                    """
                    SELECT
                        c.id,
                        c.organization_id
                    FROM resident_family_consents c
                    JOIN users u
                      ON u.id = c.family_representative_id
                    JOIN roles r
                      ON r.id = u.role_id
                    WHERE c.resident_id = %s
                      AND c.family_representative_id = %s
                      AND c.status = 'active'
                      AND u.is_active = TRUE
                      AND r.name = 'family_representative'
                    ORDER BY c.granted_at DESC
                    LIMIT 1
                    FOR SHARE OF c
                    """,
                    (resident_id, actor_user_id),
                ).fetchone()

                if consent is None:
                    raise PermissionError(
                        "Active consent is required for this resident"
                    )

                consent_id, organization_id = consent

                row = connection.execute(
                    f"""
                    INSERT INTO resident_remote_checkins (
                        id,
                        consent_id,
                        resident_id,
                        organization_id,
                        actor_user_id,
                        wellbeing_status,
                        notes,
                        recorded_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        CURRENT_TIMESTAMP
                    )
                    RETURNING {_CHECKIN_COLUMNS}
                    """,
                    (
                        str(uuid4()),
                        consent_id,
                        resident_id,
                        organization_id,
                        actor_user_id,
                        wellbeing_status,
                        notes,
                    ),
                ).fetchone()

        return _to_checkin(row)

    def list_checkins(
        self,
        user: UserContext,
        resident_id: str,
    ) -> list[RemoteCheckIn]:
        with get_connection() as connection:

            if user.role == Role.FAMILY_REPRESENTATIVE:
                active_consent = connection.execute(
                    """
                    SELECT 1
                    FROM resident_family_consents
                    WHERE resident_id = %s
                      AND family_representative_id = %s
                      AND status = 'active'
                    LIMIT 1
                    """,
                    (resident_id, user.user_id),
                ).fetchone()

                if active_consent is None:
                    raise PermissionError(
                        "Active consent is required to view check-ins"
                    )

                rows = connection.execute(
                    f"""
                    SELECT {_QUALIFIED_CHECKIN_COLUMNS}
                    FROM resident_remote_checkins c
                    WHERE c.resident_id = %s
                      AND EXISTS (
                          SELECT 1
                          FROM resident_family_consents consent
                          WHERE consent.resident_id = c.resident_id
                            AND consent.organization_id = c.organization_id
                            AND consent.family_representative_id = %s
                            AND consent.status = 'active'
                      )
                    ORDER BY c.recorded_at DESC, c.id DESC
                    """,
                    (resident_id, user.user_id),
                ).fetchall()

            elif user.role == Role.CARE_HOME_STAFF:
                allowed = connection.execute(
                    """
                    SELECT 1
                    FROM resident_family_consents c
                    JOIN user_organizations uo
                      ON uo.organization_id = c.organization_id
                    JOIN users u ON u.id = uo.user_id
                    JOIN roles r ON r.id = u.role_id
                    WHERE c.resident_id = %s
                      AND u.id = %s
                      AND u.is_active = TRUE
                      AND r.name = 'care_home_staff'
                    LIMIT 1
                    """,
                    (resident_id, user.user_id),
                ).fetchone()

                if allowed is None:
                    raise PermissionError(
                        "You are not authorized for this resident"
                    )

                rows = connection.execute(
                    f"""
                    SELECT {_CHECKIN_COLUMNS}
                    FROM resident_remote_checkins
                    WHERE resident_id = %s
                      AND organization_id IN (
                          SELECT DISTINCT consent.organization_id
                          FROM resident_family_consents consent
                          JOIN user_organizations uo
                            ON uo.organization_id = consent.organization_id
                          JOIN users u ON u.id = uo.user_id
                          JOIN roles r ON r.id = u.role_id
                          WHERE consent.resident_id = %s
                            AND u.id = %s
                            AND u.is_active = TRUE
                            AND r.name = 'care_home_staff'
                      )
                    ORDER BY recorded_at DESC, id DESC
                    """,
                    (resident_id, resident_id, user.user_id),
                ).fetchall()

            elif user.role == Role.CARELIFE_ADMIN:
                rows = connection.execute(
                    f"""
                    SELECT {_CHECKIN_COLUMNS}
                    FROM resident_remote_checkins
                    WHERE resident_id = %s
                    ORDER BY recorded_at DESC, id DESC
                    """,
                    (resident_id,),
                ).fetchall()

            else:
                raise PermissionError(
                    "You do not have access to these check-ins"
                )

        return [_to_checkin(row) for row in rows]