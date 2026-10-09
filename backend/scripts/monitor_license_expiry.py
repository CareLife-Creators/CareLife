
import logging

from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.core.config import get_settings
from app.infrastructure.repositories.organization_repository import (
    PostgresOrganizationRepository,
)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    settings = get_settings()

    repository = PostgresOrganizationRepository()

    service = OrganizationVerificationService(
        repository=repository,
    )

    result = service.monitor_license_expiry(
        reminder_days=settings.license_expiry_reminder_days,
    )

    print(
        "Organizations marked expired:",
        result["expired_organizations"],
    )

    print(
        "Expiry reminders created:",
        result["reminders_created"],
    )

    if result["reminder_failed"]:
        raise SystemExit(
            "Expiry status updates were saved, but reminder creation failed."
        )


if __name__ == "__main__":
    main()