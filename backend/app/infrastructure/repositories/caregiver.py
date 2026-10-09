
from enum import Enum
from uuid import uuid4

from app.application.interfaces.caregiver import CaregiverRepository
from app.domain.entities.caregiver import (
    CaregiverDocument,
    CaregiverDocumentType,
    CaregiverProfile,
    CaregiverPublicProfile,
    CaregiverType,
    CaregiverVerificationStatus,
)
from app.infrastructure.database.connection import get_connection


class PostgresCaregiverRepository(CaregiverRepository):

    @staticmethod
    def _profile_query():
        return """
            SELECT
                p.user_id,
                u.full_name,
                u.phone,
                p.service_type,
                p.bio,
                p.experience_years,
                p.location,
                p.verification_status,
                p.review_message,
                p.reviewed_at,
                p.created_at,
                p.updated_at
            FROM caregiver_profiles p
            JOIN users u ON u.id = p.user_id
        """

    @staticmethod
    def _to_public_profile(row) -> CaregiverPublicProfile:
        return CaregiverPublicProfile(
            caregiver_id=row[0],
            full_name=row[1],
            service_type=CaregiverType(row[2]),
            bio=row[3],
            experience_years=row[4],
            location=row[5],
        )

    @staticmethod
    def _to_profile(connection, row) -> CaregiverProfile:
        document_rows = connection.execute(
            """
            SELECT
                id,
                document_type,
                document_reference,
                submitted_at
            FROM caregiver_documents
            WHERE caregiver_user_id = %s
            ORDER BY submitted_at DESC, id DESC
            """,
            (row[0],),
        ).fetchall()

        documents = [
            CaregiverDocument(
                id=document_row[0],
                document_type=CaregiverDocumentType(document_row[1]),
                document_reference=document_row[2],
                submitted_at=document_row[3],
            )
            for document_row in document_rows
        ]

        return CaregiverProfile(
            user_id=row[0],
            full_name=row[1],
            phone=row[2],
            service_type=CaregiverType(row[3]),
            bio=row[4],
            experience_years=row[5],
            location=row[6],
            verification_status=CaregiverVerificationStatus(row[7]),
            review_message=row[8],
            reviewed_at=row[9],
            created_at=row[10],
            updated_at=row[11],
            documents=documents,
        )

    def create_profile(
        self,
        user_id: str,
        service_type: CaregiverType,
        bio: str | None,
        experience_years: int,
        location: str | None,
    ) -> CaregiverProfile:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO caregiver_profiles (
                        user_id,
                        service_type,
                        bio,
                        experience_years,
                        location,
                        verification_status,
                        created_at,
                        updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, 'pending', NOW(), NOW())
                    """,
                    (
                        user_id,
                        service_type.value,
                        bio,
                        experience_years,
                        location,
                    ),
                )

        profile = self.get_profile(user_id)

        if profile is None:
            raise RuntimeError("Created caregiver profile was not found")

        return profile

    def get_profile(
        self,
        user_id: str,
    ) -> CaregiverProfile | None:
        with get_connection() as connection:
            row = connection.execute(
                self._profile_query() + " WHERE p.user_id = %s",
                (user_id,),
            ).fetchone()

            if row is None:
                return None

            return self._to_profile(connection, row)

    def update_profile(
        self,
        user_id: str,
        updates: dict[str, object],
    ) -> CaregiverProfile | None:
        allowed_fields = {
            "service_type": "service_type",
            "bio": "bio",
            "experience_years": "experience_years",
            "location": "location",
        }

        selected = {
            key: value
            for key, value in updates.items()
            if key in allowed_fields
        }

        if not selected:
            return self.get_profile(user_id)

        assignments = []
        values = []

        for key, value in selected.items():
            assignments.append(f"{allowed_fields[key]} = %s")

            if isinstance(value, Enum):
                value = value.value

            values.append(value)

        assignments.extend(
            [
                "verification_status = 'pending'",
                "review_message = NULL",
                "reviewed_by = NULL",
                "reviewed_at = NULL",
                "updated_at = CURRENT_TIMESTAMP",
            ]
        )

        with get_connection() as connection:
            with connection.transaction():
                result = connection.execute(
                    f"""
                    UPDATE caregiver_profiles
                    SET {", ".join(assignments)}
                    WHERE user_id = %s
                    """,
                    (*values, user_id),
                )

                if result.rowcount == 0:
                    return None

        return self.get_profile(user_id)

    def submit_document(
        self,
        user_id: str,
        document_type: str,
        document_reference: str,
    ) -> CaregiverProfile | None:
        with get_connection() as connection:
            with connection.transaction():
                exists = connection.execute(
                    """
                    SELECT 1
                    FROM caregiver_profiles
                    WHERE user_id = %s
                    """,
                    (user_id,),
                ).fetchone()

                if exists is None:
                    return None

                connection.execute(
                    """
                    INSERT INTO caregiver_documents (
                        id,
                        caregiver_user_id,
                        document_type,
                        document_reference,
                        submitted_at
                    )
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    (
                        str(uuid4()),
                        user_id,
                        document_type,
                        document_reference,
                    ),
                )

                connection.execute(
                    """
                    UPDATE caregiver_profiles
                    SET
                        verification_status = 'pending',
                        review_message = NULL,
                        reviewed_by = NULL,
                        reviewed_at = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )

        return self.get_profile(user_id)

    def list_pending_profiles(self) -> list[CaregiverProfile]:
        with get_connection() as connection:
            rows = connection.execute(
                self._profile_query()
                + """
                    WHERE p.verification_status = 'pending'
                    ORDER BY p.created_at ASC, p.user_id ASC
                """
            ).fetchall()

            return [
                self._to_profile(connection, row)
                for row in rows
            ]

    def review_profile(
        self,
        caregiver_id: str,
        status: CaregiverVerificationStatus,
        reviewer_id: str,
        message: str | None,
    ) -> CaregiverProfile | None:
        with get_connection() as connection:
            with connection.transaction():
                updated = connection.execute(
                    """
                    UPDATE caregiver_profiles
                    SET
                        verification_status = %s,
                        reviewed_by = %s,
                        review_message = %s,
                        reviewed_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                      AND verification_status = 'pending'
                    RETURNING user_id
                    """,
                    (
                        status.value,
                        reviewer_id,
                        message,
                        caregiver_id,
                    ),
                ).fetchone()

                if updated is None:
                    return None

        return self.get_profile(caregiver_id)

    def list_public_profiles(
        self,
        search: str | None = None,
        location: str | None = None,
        service_type: CaregiverType | None = None,
    ) -> list[CaregiverPublicProfile]:
        search_pattern = (
            f"%{search.strip()}%"
            if search and search.strip()
            else None
        )

        location_pattern = (
            f"%{location.strip()}%"
            if location and location.strip()
            else None
        )

        service_value = (
            service_type.value
            if service_type is not None
            else None
        )

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    p.user_id,
                    u.full_name,
                    p.service_type,
                    p.bio,
                    p.experience_years,
                    p.location
                FROM caregiver_profiles p
                JOIN users u ON u.id = p.user_id
                WHERE p.verification_status = 'approved'
                  AND (
                      %s IS NULL
                      OR u.full_name ILIKE %s
                      OR COALESCE(p.bio, '') ILIKE %s
                  )
                  AND (
                      %s IS NULL
                      OR COALESCE(p.location, '') ILIKE %s
                  )
                  AND (
                      %s IS NULL
                      OR p.service_type = %s
                  )
                ORDER BY u.full_name ASC, p.user_id ASC
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    location_pattern,
                    location_pattern,
                    service_value,
                    service_value,
                ),
            ).fetchall()

        return [
            self._to_public_profile(row)
            for row in rows
        ]

    def get_public_profile(
        self,
        caregiver_id: str,
    ) -> CaregiverPublicProfile | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    p.user_id,
                    u.full_name,
                    p.service_type,
                    p.bio,
                    p.experience_years,
                    p.location
                FROM caregiver_profiles p
                JOIN users u ON u.id = p.user_id
                WHERE p.user_id = %s
                  AND p.verification_status = 'approved'
                """,
                (caregiver_id,),
            ).fetchone()

        if row is None:
            return None

        return self._to_public_profile(row)