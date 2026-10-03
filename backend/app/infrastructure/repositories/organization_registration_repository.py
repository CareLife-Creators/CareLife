from app.domain.entities.organization_registration import (
    OrganizationRegistration,
    RegistrationStatus,
)
from app.infrastructure.database.connection import get_connection


class PostgresOrganizationRegistrationRepository:
    def create(
        self,
        registration: OrganizationRegistration,
    ) -> OrganizationRegistration:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO organization_registrations (
                        organization_id,
                        organization_name,
                        organization_type,
                        license_number,
                        license_expiry_date,
                        submitted_by,
                        status,
                        submitted_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        registration.organization_id,
                        registration.organization_name,
                        registration.organization_type,
                        registration.license_number,
                        registration.license_expiry_date,
                        registration.submitted_by,
                        registration.status.value,
                        registration.submitted_at,
                    ),
                )

                connection.execute(
                    """
                    INSERT INTO organization_verifications (
                        organization_id,
                        organization_name,
                        organization_type,
                        status,
                        submitted_at,
                        updated_at,
                        message
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        registration.organization_id,
                        registration.organization_name,
                        registration.organization_type,
                        RegistrationStatus.PENDING.value,
                        registration.submitted_at,
                        registration.submitted_at,
                        "Registration submitted for verification.",
                    ),
                )

        return registration
