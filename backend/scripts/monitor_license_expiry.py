
import logging

from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.core.config import get_settings
from app.infrastructure.email.license_expiry_email import (
    LicenseExpiryEmailSender,
)
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

    sender = LicenseExpiryEmailSender(settings)

    service = OrganizationVerificationService(
        repository=repository,
    )

    result = service.monitor_license_expiry(
        reminder_days=settings.license_expiry_reminder_days,
    )

    emails_sent = 0
    email_failures = 0
    for reminder in repository.get_pending_license_expiry_emails():
        try:
            sender.send_license_expiry_reminder(
                email=reminder["email"],
                organization_name=reminder["organization_name"],
                document_type=reminder["document_type"],
                expires_on=reminder["expires_on"],
                message_text=reminder["message"],
            )
            repository.mark_license_expiry_email_sent(
                reminder["notification_id"],
            )
            emails_sent += 1
        except Exception:
            logging.exception(
                "Could not send organization license expiry email to %s",
                reminder["email"],
            )
            email_failures += 1

    print(
        "Organizations marked expired:",
        result["expired_organizations"],
    )

    print(
        "Expiry reminders created:",
        result["reminders_created"],
    )

    print("Expiry reminder emails sent:", emails_sent)
    print("Expiry reminder email failures:", email_failures)

    if result["reminder_failed"] or email_failures:
        raise SystemExit(
            "Expiry monitoring completed with failures; failed emails remain "
            "queued for the next run."
        )


if __name__ == "__main__":
    main()
