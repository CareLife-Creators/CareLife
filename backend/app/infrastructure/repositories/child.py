from app.application.interfaces.child import ChildRepository
from app.domain.entities.child import (
    Child,
    ChildContact,
    ContactType,
    OrphanageOutcome,
    OutcomeStatus,
    OutcomeType,
)
from app.infrastructure.database.connection import get_connection


class PostgresChildRepository(ChildRepository):
    def organization_is_orphanage(
        self,
        organization_id: str,
    ) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM organizations
                WHERE id = %s
                  AND organization_type = 'orphanage'
                """,
                (organization_id,),
            ).fetchone()

        return row is not None

    def create(self, child: Child) -> Child:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO children (
                        id,
                        parent_id,
                        full_name,
                        date_of_birth,
                        gender,
                        allergies,
                        medical_notes,
                        orphanage_organization_id,
                        daycare_organization_id,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        child.id,
                        child.parent_id,
                        child.full_name,
                        child.date_of_birth,
                        child.gender,
                        child.allergies,
                        child.medical_notes,
                        child.orphanage_organization_id,
                        child.daycare_organization_id,
                        child.created_at,
                        child.updated_at,
                    ),
                )

        return self.get(child.id)  # type: ignore[return-value]

    def list_by_orphanage(
        self,
        organization_id: str,
    ) -> list[Child]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    parent_id,
                    full_name,
                    date_of_birth,
                    gender,
                    allergies,
                    medical_notes,
                    orphanage_organization_id,
                    daycare_organization_id,
                    created_at,
                    updated_at
                FROM children
                WHERE orphanage_organization_id = %s
                ORDER BY full_name
                """,
                (organization_id,),
            ).fetchall()

        return [self._child_from_row(row) for row in rows]

    def list_by_parent(
        self,
        parent_id: str,
    ) -> list[Child]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    parent_id,
                    full_name,
                    date_of_birth,
                    gender,
                    allergies,
                    medical_notes,
                    orphanage_organization_id,
                    daycare_organization_id,
                    created_at,
                    updated_at
                FROM children
                WHERE parent_id = %s
                ORDER BY full_name
                """,
                (parent_id,),
            ).fetchall()

        return [self._child_from_row(row) for row in rows]

    def get(
        self,
        child_id: str,
    ) -> Child | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    parent_id,
                    full_name,
                    date_of_birth,
                    gender,
                    allergies,
                    medical_notes,
                    orphanage_organization_id,
                    daycare_organization_id,
                    created_at,
                    updated_at
                FROM children
                WHERE id = %s
                """,
                (child_id,),
            ).fetchone()

        if row is None:
            return None

        return self._child_from_row(row)

    def update(
        self,
        child: Child,
    ) -> Child | None:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    UPDATE children
                    SET
                        full_name = %s,
                        date_of_birth = %s,
                        gender = %s,
                        allergies = %s,
                        medical_notes = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (
                        child.full_name,
                        child.date_of_birth,
                        child.gender,
                        child.allergies,
                        child.medical_notes,
                        child.updated_at,
                        child.id,
                    ),
                )

        return self.get(child.id)

    def delete(
        self,
        child_id: str,
    ) -> bool:
        with get_connection() as connection:
            with connection.transaction():
                result = connection.execute(
                    """
                    DELETE FROM children
                    WHERE id = %s
                    RETURNING id
                    """,
                    (child_id,),
                ).fetchone()

        return result is not None

    # ---------------------------------------------------------
    # Orphanage outcomes
    # ---------------------------------------------------------

    def create_outcome(
        self,
        outcome: OrphanageOutcome,
    ) -> OrphanageOutcome:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO orphanage_outcomes (
                        id,
                        child_id,
                        organization_id,
                        outcome_type,
                        outcome_status,
                        outcome_date,
                        notes,
                        created_by,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        outcome.id,
                        outcome.child_id,
                        outcome.organization_id,
                        outcome.outcome_type.value,
                        outcome.outcome_status.value,
                        outcome.outcome_date,
                        outcome.notes,
                        outcome.created_by,
                        outcome.created_at,
                        outcome.updated_at,
                    ),
                )

        return self.get_outcome(outcome.id)  # type: ignore[return-value]

    def list_outcomes(
        self,
        child_id: str,
    ) -> list[OrphanageOutcome]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    child_id,
                    organization_id,
                    outcome_type,
                    outcome_status,
                    outcome_date,
                    notes,
                    created_by,
                    created_at,
                    updated_at
                FROM orphanage_outcomes
                WHERE child_id = %s
                ORDER BY outcome_date DESC, created_at DESC
                """,
                (child_id,),
            ).fetchall()

        return [self._outcome_from_row(row) for row in rows]

    def get_outcome(
        self,
        outcome_id: str,
    ) -> OrphanageOutcome | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    child_id,
                    organization_id,
                    outcome_type,
                    outcome_status,
                    outcome_date,
                    notes,
                    created_by,
                    created_at,
                    updated_at
                FROM orphanage_outcomes
                WHERE id = %s
                """,
                (outcome_id,),
            ).fetchone()

        if row is None:
            return None

        return self._outcome_from_row(row)

    def update_outcome(
        self,
        outcome: OrphanageOutcome,
    ) -> OrphanageOutcome | None:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    UPDATE orphanage_outcomes
                    SET
                        outcome_status = %s,
                        outcome_date = %s,
                        notes = %s,
                        updated_at = %s
                    WHERE id = %s
                    """,
                    (
                        outcome.outcome_status.value,
                        outcome.outcome_date,
                        outcome.notes,
                        outcome.updated_at,
                        outcome.id,
                    ),
                )

        return self.get_outcome(outcome.id)

    def delete_outcome(
        self,
        outcome_id: str,
    ) -> bool:
        with get_connection() as connection:
            with connection.transaction():
                result = connection.execute(
                    """
                    DELETE FROM orphanage_outcomes
                    WHERE id = %s
                    RETURNING id
                    """,
                    (outcome_id,),
                ).fetchone()

        return result is not None

    # ---------------------------------------------------------
    # CAR-113 child contacts
    # ---------------------------------------------------------

    def create_contact(
        self,
        contact: ChildContact,
    ) -> ChildContact:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO child_contacts (
                        id,
                        child_id,
                        contact_type,
                        full_name,
                        relationship_to_child,
                        phone,
                        email,
                        address,
                        created_by,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        contact.id,
                        contact.child_id,
                        contact.contact_type.value,
                        contact.full_name,
                        contact.relationship_to_child,
                        contact.phone,
                        contact.email,
                        contact.address,
                        contact.created_by,
                        contact.created_at,
                        contact.updated_at,
                    ),
                )

        return self.get_contact(contact.id)  # type: ignore[return-value]

    def get_contact(
        self,
        contact_id: str,
    ) -> ChildContact | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    child_id,
                    contact_type,
                    full_name,
                    relationship_to_child,
                    phone,
                    email,
                    address,
                    created_by,
                    created_at,
                    updated_at
                FROM child_contacts
                WHERE id = %s
                """,
                (contact_id,),
            ).fetchone()

        if row is None:
            return None

        return self._contact_from_row(row)

    def list_contacts(
        self,
        child_id: str,
        contact_type: str,
    ) -> list[ChildContact]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    child_id,
                    contact_type,
                    full_name,
                    relationship_to_child,
                    phone,
                    email,
                    address,
                    created_by,
                    created_at,
                    updated_at
                FROM child_contacts
                WHERE child_id = %s
                  AND contact_type = %s
                ORDER BY full_name
                """,
                (
                    child_id,
                    contact_type,
                ),
            ).fetchall()

        return [self._contact_from_row(row) for row in rows]

    # ---------------------------------------------------------
    # Mapping helpers
    # ---------------------------------------------------------

    @staticmethod
    def _child_from_row(row) -> Child:
        return Child(
            id=row[0],
            parent_id=row[1],
            full_name=row[2],
            date_of_birth=row[3],
            gender=row[4],
            allergies=row[5],
            medical_notes=row[6],
            orphanage_organization_id=row[7],
            daycare_organization_id=row[8],
            created_at=row[9],
            updated_at=row[10],
        )

    @staticmethod
    def _outcome_from_row(row) -> OrphanageOutcome:
        return OrphanageOutcome(
            id=row[0],
            child_id=row[1],
            organization_id=row[2],
            outcome_type=OutcomeType(row[3]),
            outcome_status=OutcomeStatus(row[4]),
            outcome_date=row[5],
            notes=row[6],
            created_by=row[7],
            created_at=row[8],
            updated_at=row[9],
        )

    @staticmethod
    def _contact_from_row(row) -> ChildContact:
        return ChildContact(
            id=row[0],
            child_id=row[1],
            contact_type=ContactType(row[2]),
            full_name=row[3],
            relationship_to_child=row[4],
            phone=row[5],
            email=row[6],
            address=row[7],
            created_by=row[8],
            created_at=row[9],
            updated_at=row[10],
        )