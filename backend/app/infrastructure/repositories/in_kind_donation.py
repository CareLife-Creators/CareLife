from decimal import Decimal

from app.application.interfaces.in_kind_donation import (
    InKindDonationRepository,
)
from app.domain.entities.in_kind_donation import (
    InKindDonationPledge,
    InKindDonationStatus,
)
from app.domain.entities.user_context import Role
from app.infrastructure.database.connection import get_connection


_PLEDGE_SELECT = """
    SELECT
        p.id,
        p.need_id,
        n.title,
        n.organization_id,
        o.name,
        p.donor_id,
        p.quantity,
        n.unit,
        p.notes,
        p.status,
        p.received_by,
        p.received_at,
        p.allocated_by,
        p.allocated_at,
        p.created_at,
        p.updated_at
    FROM in_kind_donation_pledges p
    JOIN donation_needs n ON n.id = p.need_id
    JOIN organizations o ON o.id = n.organization_id
"""

_AUTHORIZATION_SELECT = """
    SELECT 1
    FROM organizations o
    JOIN user_organizations uo
        ON uo.organization_id = o.id
    JOIN users u
        ON u.id = uo.user_id
    WHERE o.id = %s
      AND u.id = %s
      AND u.is_active = TRUE
      AND (
          (o.organization_type = 'daycare'
              AND %s = 'daycare_staff')
          OR
          (o.organization_type = 'orphanage'
              AND %s = 'orphanage_staff')
          OR
          (o.organization_type = 'elderly_care'
              AND %s = 'care_home_staff')
      )
"""


class PostgresInKindDonationRepository(InKindDonationRepository):
    """Persist in-kind pledges and enforce their valid status transitions."""

    def is_authorized_organization_staff(
        self,
        organization_id: str,
        user_id: str,
        role: Role,
    ) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                _AUTHORIZATION_SELECT,
                (organization_id, user_id, role.value, role.value, role.value),
            ).fetchone()

        return row is not None

    @staticmethod
    def _assert_staff_access(
        connection,
        organization_id: str,
        user_id: str,
        role: Role,
    ) -> None:
        row = connection.execute(
            _AUTHORIZATION_SELECT + " FOR SHARE OF o, uo, u",
            (organization_id, user_id, role.value),
        ).fetchone()

        if row is None:
            raise PermissionError(
                "Authorized staff membership for this organization is required"
            )

    def create_pledge(
        self,
        pledge: InKindDonationPledge,
        donor_id: str,
    ) -> InKindDonationPledge:
        with get_connection() as connection:
            with connection.transaction():
                need = connection.execute(
                    """
                    SELECT n.id
                    FROM donation_needs n
                    JOIN organizations o
                        ON o.id = n.organization_id
                    JOIN verification_statuses vs
                        ON vs.id = o.status_id
                    WHERE n.id = %s
                      AND n.need_type = 'in_kind'
                      AND n.is_active = TRUE
                      AND vs.name = 'verified'
                    FOR SHARE OF n, o
                    """,
                    (pledge.need_id,),
                ).fetchone()

                if need is None:
                    raise LookupError(
                        "Active in-kind donation need not found"
                    )

                donor = connection.execute(
                    """
                    SELECT u.id
                    FROM users u
                    JOIN roles r ON r.id = u.role_id
                    WHERE u.id = %s
                      AND u.is_active = TRUE
                      AND r.name = 'donor_supporter'
                    FOR SHARE OF u
                    """,
                    (donor_id,),
                ).fetchone()

                if donor is None:
                    raise PermissionError(
                        "An active donor-supporter account is required"
                    )

                connection.execute(
                    """
                    INSERT INTO in_kind_donation_pledges (
                        id,
                        need_id,
                        donor_id,
                        quantity,
                        notes,
                        status,
                        received_by,
                        received_at,
                        allocated_by,
                        allocated_at,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        NULL, NULL, NULL, NULL, %s, %s
                    )
                    """,
                    (
                        pledge.id,
                        pledge.need_id,
                        donor_id,
                        pledge.quantity,
                        pledge.notes,
                        InKindDonationStatus.PLEDGED.value,
                        pledge.created_at,
                        pledge.updated_at,
                    ),
                )

        saved = self.get_pledge_for_donor(
            pledge.id,
            donor_id,
        )

        if saved is None:
            raise RuntimeError(
                "Pledge was created but could not be reloaded"
            )

        return saved

    def list_pledges_for_donor(
        self,
        donor_id: str,
    ) -> list[InKindDonationPledge]:
        with get_connection() as connection:
            rows = connection.execute(
                _PLEDGE_SELECT
                + """
                WHERE p.donor_id = %s
                ORDER BY p.created_at DESC, p.id DESC
                """,
                (donor_id,),
            ).fetchall()

        return [self._pledge_from_row(row) for row in rows]

    def get_pledge_for_donor(
        self,
        pledge_id: str,
        donor_id: str,
    ) -> InKindDonationPledge | None:
        with get_connection() as connection:
            row = connection.execute(
                _PLEDGE_SELECT
                + " WHERE p.id = %s AND p.donor_id = %s",
                (pledge_id, donor_id),
            ).fetchone()

        return self._pledge_from_row(row)

    def list_pledges_for_organization(
        self,
        organization_id: str,
    ) -> list[InKindDonationPledge]:
        with get_connection() as connection:
            rows = connection.execute(
                _PLEDGE_SELECT
                + """
                WHERE n.organization_id = %s
                ORDER BY p.created_at DESC, p.id DESC
                """,
                (organization_id,),
            ).fetchall()

        return [self._pledge_from_row(row) for row in rows]

    def get_pledge_for_organization(
        self,
        organization_id: str,
        pledge_id: str,
    ) -> InKindDonationPledge | None:
        with get_connection() as connection:
            row = connection.execute(
                _PLEDGE_SELECT
                + """
                WHERE n.organization_id = %s
                  AND p.id = %s
                """,
                (organization_id, pledge_id),
            ).fetchone()

        return self._pledge_from_row(row)

    def transition_pledge_status(
        self,
        organization_id: str,
        pledge_id: str,
        new_status: InKindDonationStatus,
        user_id: str,
        role: Role,
    ) -> InKindDonationPledge | None:
        with get_connection() as connection:
            with connection.transaction():
                self._assert_staff_access(
                    connection,
                    organization_id,
                    user_id,
                    role,
                )

                row = connection.execute(
                    _PLEDGE_SELECT
                    + """
                    WHERE n.organization_id = %s
                      AND p.id = %s
                    FOR UPDATE OF p
                    """,
                    (organization_id, pledge_id),
                ).fetchone()

                if row is None:
                    return None

                current_status = InKindDonationStatus(row[9])

                if (
                    current_status == InKindDonationStatus.PLEDGED
                    and new_status == InKindDonationStatus.RECEIVED
                ):
                    cursor = connection.execute(
                        """
                        UPDATE in_kind_donation_pledges
                        SET status = %s,
                            received_by = %s,
                            received_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s AND status = %s
                        """,
                        (
                            new_status.value,
                            user_id,
                            pledge_id,
                            current_status.value,
                        ),
                    )

                elif (
                    current_status == InKindDonationStatus.RECEIVED
                    and new_status == InKindDonationStatus.ALLOCATED
                ):
                    cursor = connection.execute(
                        """
                        UPDATE in_kind_donation_pledges
                        SET status = %s,
                            allocated_by = %s,
                            allocated_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s AND status = %s
                        """,
                        (
                            new_status.value,
                            user_id,
                            pledge_id,
                            current_status.value,
                        ),
                    )

                else:
                    raise ValueError(
                        "Only pledged-to-received and "
                        "received-to-allocated transitions are permitted"
                    )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "Pledge status changed before this update completed"
                    )

        return self.get_pledge_for_organization(
            organization_id,
            pledge_id,
        )

    @staticmethod
    def _pledge_from_row(row) -> InKindDonationPledge | None:
        if row is None:
            return None

        return InKindDonationPledge(
            id=row[0],
            need_id=row[1],
            need_title=row[2],
            organization_id=row[3],
            organization_name=row[4],
            donor_id=row[5],
            quantity=Decimal(str(row[6])),
            unit=row[7],
            notes=row[8],
            status=InKindDonationStatus(row[9]),
            received_by=row[10],
            received_at=row[11],
            allocated_by=row[12],
            allocated_at=row[13],
            created_at=row[14],
            updated_at=row[15],
        )
