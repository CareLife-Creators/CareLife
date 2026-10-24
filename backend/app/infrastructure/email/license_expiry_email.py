from email.message import EmailMessage
import logging
import smtplib

from app.core.config import Settings


logger = logging.getLogger(__name__)


class LicenseExpiryEmailSender:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send_license_expiry_reminder(
        self,
        email: str,
        organization_name: str,
        document_type: str,
        expires_on: str,
        message_text: str,
    ) -> None:
        if self.settings.email_mode != "smtp":
            raise RuntimeError(
                "License expiry email delivery requires EMAIL_MODE=smtp."
            )
        if not self.settings.smtp_host:
            raise ValueError("SMTP_HOST is required when EMAIL_MODE=smtp")

        message = EmailMessage()
        document_name = document_type.replace("_", " ").strip().title()
        message["Subject"] = (
            f"CareLife organization {document_name.lower()} expiry reminder"
        )
        message["From"] = self.settings.email_from
        message["To"] = email
        message.set_content(
            f"Hello,\n\n{message_text}\n\n"
            f"Organization: {organization_name}\n"
            f"{document_name} expiry date: {expires_on}\n\n"
            "Please sign in to CareLife and submit your updated organization "
            "documents for review before this date. CareLife verification "
            "does not replace government licensing or legal certification."
        )

        with smtplib.SMTP(
            self.settings.smtp_host,
            self.settings.smtp_port,
            timeout=20,
        ) as server:
            server.starttls()
            if self.settings.smtp_username and self.settings.smtp_password_value:
                server.login(
                    self.settings.smtp_username,
                    self.settings.smtp_password_value,
                )
            server.send_message(message)
