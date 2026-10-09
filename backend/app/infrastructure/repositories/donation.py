from decimal import Decimal
from enum import Enum

from app.application.interfaces.donation import DonationRepository
from app.domain.entities.donation import DonationCampaign, DonationNeed, DonationNeedType
from app.domain.entities.user_context import Role
from app.infrastructure.database.connection import get_connection


_CAMPAIGN_SELECT = """
    SELECT c.id, c.organization_id, o.name, o.organization_type,
           c.title, c.description, c.target_amount, c.currency,
           c.utilized_amount, c.is_active, c.created_at, c.updated_at
    FROM donation_campaigns c
    JOIN organizations o ON o.id = c.organization_id
"""

_NEED_SELECT = """
    SELECT n.id, n.organization_id, o.name, o.organization_type,
           n.title, n.description, n.category, n.need_type,
           n.target_amount, n.target_quantity, n.unit,
           n.is_active, n.created_at, n.updated_at
    FROM donation_needs n
    JOIN organizations o ON o.id = n.organization_id
"""

_AUTHORIZATION_SELECT = """
    SELECT 1
    FROM organizations o
    JOIN user_organizations uo ON uo.organization_id = o.id
    JOIN users u ON u.id = uo.user_id
    JOIN roles r ON r.id = u.role_id
    WHERE o.id = %s
      AND u.id = %s
      AND u.is_active = TRUE
      AND r.name = %s
      AND ((o.organization_type = 'daycare' AND r.name = 'daycare_staff')
        OR (o.organization_type = 'orphanage' AND r.name = 'orphanage_staff')
        OR (o.organization_type = 'elderly_care' AND r.name = 'care_home_staff'))
"""


class PostgresDonationRepository(DonationRepository):
    """Persistence for campaign/need records.

    The current dev branch has no successful donation/payment transaction table.
    Until one exists, received_amount is reported as zero instead of inventing
    a duplicate donation-transaction model.
    """

    def is_authorized_organization_staff(self, organization_id: str, user_id: str, role: Role) -> bool:
        with get_connection() as connection:
            row = connection.execute(_AUTHORIZATION_SELECT, (organization_id, user_id, role.value)).fetchone()
        return row is not None

    @staticmethod
    def _assert_staff_access(connection, organization_id: str, user_id: str, role: Role) -> None:
        row = connection.execute(
            _AUTHORIZATION_SELECT + " FOR SHARE OF o, uo, u",
            (organization_id, user_id, role.value),
        ).fetchone()
        if row is None:
            raise PermissionError("Authorized staff membership for this organization is required")

    def create_campaign(self, campaign: DonationCampaign, user_id: str, role: Role) -> DonationCampaign:
        with get_connection() as connection:
            with connection.transaction():
                self._assert_staff_access(connection, campaign.organization_id, user_id, role)
                connection.execute(
                    """INSERT INTO donation_campaigns
                    (id, organization_id, title, description, target_amount, currency,
                     utilized_amount, is_active, created_by, updated_by, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (campaign.id, campaign.organization_id, campaign.title, campaign.description,
                     campaign.target_amount, campaign.currency, campaign.utilized_amount,
                     campaign.is_active, user_id, user_id, campaign.created_at, campaign.updated_at),
                )
        saved = self.get_campaign_for_organization(campaign.organization_id, campaign.id)
        if saved is None:
            raise RuntimeError("Campaign was created but could not be reloaded")
        return saved

    def get_campaign_for_organization(self, organization_id: str, campaign_id: str) -> DonationCampaign | None:
        with get_connection() as connection:
            row = connection.execute(
                _CAMPAIGN_SELECT + " WHERE c.organization_id = %s AND c.id = %s",
                (organization_id, campaign_id),
            ).fetchone()
        return self._campaign_from_row(row)

    def list_campaigns_for_organization(self, organization_id: str) -> list[DonationCampaign]:
        with get_connection() as connection:
            rows = connection.execute(
                _CAMPAIGN_SELECT + " WHERE c.organization_id = %s ORDER BY c.created_at DESC",
                (organization_id,),
            ).fetchall()
        return [self._campaign_from_row(row) for row in rows]

    def update_campaign(self, organization_id: str, campaign_id: str, changes: dict[str, object], user_id: str, role: Role) -> DonationCampaign | None:
        columns = {"title": "title", "description": "description", "target_amount": "target_amount",
                   "currency": "currency", "utilized_amount": "utilized_amount", "is_active": "is_active"}
        assignments, values = self._update_assignments(changes, columns)
        assignments.extend(["updated_by = %s", "updated_at = CURRENT_TIMESTAMP"])
        values.extend([user_id, campaign_id, organization_id])
        with get_connection() as connection:
            with connection.transaction():
                self._assert_staff_access(connection, organization_id, user_id, role)
                cursor = connection.execute(
                    "UPDATE donation_campaigns SET " + ", ".join(assignments)
                    + " WHERE id = %s AND organization_id = %s", values
                )
                if cursor.rowcount == 0:
                    return None
        return self.get_campaign_for_organization(organization_id, campaign_id)

    def list_public_campaigns(self, organization_id: str | None = None) -> list[DonationCampaign]:
        query = (_CAMPAIGN_SELECT + " JOIN verification_statuses vs ON vs.id = o.status_id "
                 + " WHERE c.is_active = TRUE AND vs.name = 'verified'")
        params: list[object] = []
        if organization_id is not None:
            query += " AND c.organization_id = %s"
            params.append(organization_id)
        query += " ORDER BY c.created_at DESC"
        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._campaign_from_row(row) for row in rows]

    def get_public_campaign(self, campaign_id: str) -> DonationCampaign | None:
        query = (_CAMPAIGN_SELECT + " JOIN verification_statuses vs ON vs.id = o.status_id "
                 + " WHERE c.id = %s AND c.is_active = TRUE AND vs.name = 'verified'")
        with get_connection() as connection:
            row = connection.execute(query, (campaign_id,)).fetchone()
        return self._campaign_from_row(row)

    def create_need(self, need: DonationNeed, user_id: str, role: Role) -> DonationNeed:
        with get_connection() as connection:
            with connection.transaction():
                self._assert_staff_access(connection, need.organization_id, user_id, role)
                connection.execute(
                    """INSERT INTO donation_needs
                    (id, organization_id, title, description, category, need_type, target_amount,
                     target_quantity, unit, is_active, created_by, updated_by, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (need.id, need.organization_id, need.title, need.description, need.category,
                     need.need_type.value, need.target_amount, need.target_quantity, need.unit,
                     need.is_active, user_id, user_id, need.created_at, need.updated_at),
                )
        saved = self.get_need_for_organization(need.organization_id, need.id)
        if saved is None:
            raise RuntimeError("Donation need was created but could not be reloaded")
        return saved

    def get_need_for_organization(self, organization_id: str, need_id: str) -> DonationNeed | None:
        with get_connection() as connection:
            row = connection.execute(
                _NEED_SELECT + " WHERE n.organization_id = %s AND n.id = %s",
                (organization_id, need_id),
            ).fetchone()
        return self._need_from_row(row)

    def list_needs_for_organization(self, organization_id: str) -> list[DonationNeed]:
        with get_connection() as connection:
            rows = connection.execute(
                _NEED_SELECT + " WHERE n.organization_id = %s ORDER BY n.created_at DESC",
                (organization_id,),
            ).fetchall()
        return [self._need_from_row(row) for row in rows]

    def update_need(self, organization_id: str, need_id: str, changes: dict[str, object], user_id: str, role: Role) -> DonationNeed | None:
        columns = {"title": "title", "description": "description", "category": "category",
                   "need_type": "need_type", "target_amount": "target_amount",
                   "target_quantity": "target_quantity", "unit": "unit", "is_active": "is_active"}
        assignments, values = self._update_assignments(changes, columns)
        assignments.extend(["updated_by = %s", "updated_at = CURRENT_TIMESTAMP"])
        values.extend([user_id, need_id, organization_id])
        with get_connection() as connection:
            with connection.transaction():
                self._assert_staff_access(connection, organization_id, user_id, role)
                cursor = connection.execute(
                    "UPDATE donation_needs SET " + ", ".join(assignments)
                    + " WHERE id = %s AND organization_id = %s", values
                )
                if cursor.rowcount == 0:
                    return None
        return self.get_need_for_organization(organization_id, need_id)

    def list_public_needs(self, organization_id: str | None = None) -> list[DonationNeed]:
        query = (_NEED_SELECT + " JOIN verification_statuses vs ON vs.id = o.status_id "
                 + " WHERE n.is_active = TRUE AND vs.name = 'verified'")
        params: list[object] = []
        if organization_id is not None:
            query += " AND n.organization_id = %s"
            params.append(organization_id)
        query += " ORDER BY n.created_at DESC"
        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._need_from_row(row) for row in rows]

    def get_public_need(self, need_id: str) -> DonationNeed | None:
        query = (_NEED_SELECT + " JOIN verification_statuses vs ON vs.id = o.status_id "
                 + " WHERE n.id = %s AND n.is_active = TRUE AND vs.name = 'verified'")
        with get_connection() as connection:
            row = connection.execute(query, (need_id,)).fetchone()
        return self._need_from_row(row)

    @staticmethod
    def _update_assignments(changes: dict[str, object], allowed_columns: dict[str, str]) -> tuple[list[str], list[object]]:
        if not changes:
            raise ValueError("At least one field must be updated")
        unknown = set(changes) - set(allowed_columns)
        if unknown:
            raise ValueError("An unsupported field was supplied")
        assignments: list[str] = []
        values: list[object] = []
        for field, value in changes.items():
            if isinstance(value, Enum):
                value = value.value
            assignments.append(f"{allowed_columns[field]} = %s")
            values.append(value)
        return assignments, values

    @staticmethod
    def _campaign_from_row(row) -> DonationCampaign | None:
        if row is None:
            return None
        target = Decimal(str(row[6]))
        received = Decimal("0.00")  # No successful donation transaction model exists on dev yet.
        return DonationCampaign(
            id=row[0], organization_id=row[1], organization_name=row[2], organization_type=row[3],
            title=row[4], description=row[5], target_amount=target, currency=row[7],
            utilized_amount=Decimal(str(row[8])), received_amount=received,
            remaining_amount=max(target - received, Decimal("0.00")), is_active=row[9],
            created_at=row[10], updated_at=row[11],
        )

    @staticmethod
    def _need_from_row(row) -> DonationNeed | None:
        if row is None:
            return None
        return DonationNeed(
            id=row[0], organization_id=row[1], organization_name=row[2], organization_type=row[3],
            title=row[4], description=row[5], category=row[6], need_type=DonationNeedType(row[7]),
            target_amount=Decimal(str(row[8])) if row[8] is not None else None,
            target_quantity=Decimal(str(row[9])) if row[9] is not None else None,
            unit=row[10], is_active=row[11], created_at=row[12], updated_at=row[13],
        )
