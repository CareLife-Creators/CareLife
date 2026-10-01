from email.message import EmailMessage
import logging
import smtplib

from app.core.config import Settings


logger = logging.getLogger(__name__)


class ConsolePasswordResetEmailSender:
    def send_password_reset(self, email: str, reset_link: str) -> None:
        logger.info(
            "Password reset requested for %s. Reset link: %s",
            email,
            reset_link,
        )


class SmtpPasswordResetEmailSender:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send_password_reset(self, email: str, reset_link: str) -> None:
        if not self.settings.smtp_host:
            raise ValueError("SMTP_HOST is required when EMAIL_MODE=smtp")

        message = EmailMessage()
        message["Subject"] = "CareLife Password Reset"
        message["From"] = self.settings.email_from
        message["To"] = email

        message.set_content(
            "You requested a password reset for your CareLife account.\n\n"
            f"Reset your password using this link:\n{reset_link}\n\n"
            "This link is time-limited and can only be used once."
        )

        with smtplib.SMTP(
            self.settings.smtp_host,
            self.settings.smtp_port,
        ) as server:
            server.starttls()

            if self.settings.smtp_username and self.settings.smtp_password_value:
                server.login(
                    self.settings.smtp_username,
                    self.settings.smtp_password_value,
                )

            server.send_message(message)


def build_password_reset_email_sender(
    settings: Settings,
) -> ConsolePasswordResetEmailSender | SmtpPasswordResetEmailSender:
    if settings.email_mode == "smtp":
        return SmtpPasswordResetEmailSender(settings)

    return ConsolePasswordResetEmailSender()